# network/run_node.py

import os
import sys

root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root)

import grpc
import time
import json
import socket
import queue
import random
import threading
import proto.energy_chain_pb2 as energy_chain_pb2
import proto.energy_chain_pb2_grpc as energy_chain_pb2_grpc
from concurrent import futures
from network.node_service import NodeService
from core.blockchain import Blockchain
from core.miner import construct_and_mine_block
from core.wallet import Wallet
from core.cryptography import sign_tx
from core.block import calculate_tx_hash, calculate_header_hash
from core.trade import create_trade_tx
from state.validation import validate_order_tx, ValidationContext

PORT = "58333"
DISCOVERY_TIMEOUT_SECS = 3
DIFFICULTY = 0x1F0FFFFF  # increased difficulty (compared to lab) to reduce forks
MAX_TXN_PER_BLOCK = 10

"""Logical representation of the entire node. """
class Node:
    def __init__(self, my_address):
        """
        Given a the docker address of the docker container the code runs in initializes a node.
        """
        self.address = my_address
        self.known_peers = []
        self.mempool = queue.Queue()
        self.blockchain = Blockchain()

        self.seen_transactions = set()
        self.seen_blocks = set()
        self.mining_interrupt = threading.Event()

        print(f"[IP: {self.address}] Starting Node")
        genesis_hash = calculate_header_hash(self.blockchain.get_tip().header)
        print(f"Genesis Block Hash: {genesis_hash}")

        # start the automatic faucet monitor
        if "node_a" in sys.argv or self.address.endswith(".3"):
            threading.Thread(target=self.auto_faucet_loop, daemon=True).start()

    def run(self):
        """
        Function to run node. First registers node, second executes peer discovery, and finally starts mining /
        listening for new nodes joining the network.
        """
        registration_response = self.register()

        known_peers_arr = (
            [registration_response.last_registered]
            if registration_response.last_registered
            else []
        )
        print(
            f"[IP: {self.address}] [Registration] Response known peers: {known_peers_arr}"
        )

        self.discovery(registration_response.last_registered)  # discovery process

        print(
            f"[IP: {self.address}] Final known peers before mining: {self.known_peers}"
        )

        self.listening_newnodes()  # times out after 10 seconds

        print(f"[IP: {self.address}] Node starts mining")
        miner = threading.Thread(target=self.mine_loop, args=())
        miner.start()
        # run node for as long as the threads run - should only be stopped upon keyboard interrupt
        miner.join()

    def register(self):
        """
        Registers node with network by sending registration request to registrar node. Returns registration response
        from registrar.
        """
        print(
            f"[IP: {self.address}] Registering with DNS_SEED at address: dns_seed:{PORT}"
        )
        channel = grpc.insecure_channel("dns_seed" + ":" + PORT)
        # channel = grpc.insecure_channel('localhost' + ":" + PORT)
        stub = energy_chain_pb2_grpc.RegisterStub(channel)
        response = stub.RegisterNode(
            energy_chain_pb2.RegistrationRequest(
                nVersion=1, nTime=time.time(), addrMe=self.address
            )
        )
        return response

    def discovery(self, contact_node_addr: str):
        """
        Peer discovery of other nodes in the network. Initially, function is called with the node
        that last registered with the registrar. Function is recursively called until there are no new
        nodes to contact.
        """
        # no node to contact
        if not contact_node_addr:
            return

        # contact node
        print(f"[IP: {self.address}] [Handshake] Peer IP: {contact_node_addr}")
        # create channel to node trying to contact
        channel = grpc.insecure_channel(contact_node_addr + ":" + PORT)
        handshake_stub = energy_chain_pb2_grpc.NodeServiceStub(channel)
        handshake_response = handshake_stub.GetPeers(
            energy_chain_pb2.GetPeersRequest(
                nVersion=1, nTime=time.time(), addrMe=self.address, bestHeight=0
            )
        )

        self.known_peers.append(contact_node_addr)

        # gossip
        if len(handshake_response.peer_addresses) == 0:
            self.discovery(None)
        else:
            for peer_addr in handshake_response.peer_addresses:
                if peer_addr != self.address and (not peer_addr in self.known_peers):
                    self.discovery(peer_addr)

    def listening_newnodes(self):
        """
        Function to listen for new nodes joining the network. Upon a GetPeersRequest (contact by new node),
        adds new node to list of known peers and sends response of list of known peers.
        """
        self.listener = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        energy_chain_pb2_grpc.add_NodeServiceServicer_to_server(
            NodeService(self), self.listener
        )
        self.listener.add_insecure_port(f"0.0.0.0:{PORT}")
        self.listener.start()
        time.sleep(DISCOVERY_TIMEOUT_SECS)

    def mine_loop(self):
        # sleep initially to allow docker DNS to populate and node listeners to bind
        time.sleep(2)

        while True:
            try:
                # collect valid txns from the mempool
                raw_txns = []
                while True:
                    try:
                        tx = self.mempool.get(block=False)

                        # prune if the txn is already in the chain
                        if any(
                            t.transaction_hash == tx.transaction_hash
                            for b in self.blockchain.blocks
                            for t in b.transactions
                        ):
                            continue

                        raw_txns.append(tx)
                    except queue.Empty:
                        break

                if not raw_txns and random.random() > 0.1:
                    time.sleep(5)
                    continue

                # process transactions
                txns_to_mine = []
                current_state_copy = self.blockchain.state.copy()
                active_grid_rate = current_state_copy.active_grid_rate
                # prevents duplicate faucets
                faucets_in_this_block = set()

                for tx in raw_txns:
                    if len(txns_to_mine) >= MAX_TXN_PER_BLOCK:
                        break

                    if tx.HasField("grid_rate_tx"):
                        active_grid_rate = tx.grid_rate_tx
                        txns_to_mine.append(tx)
                        continue

                    if tx.HasField("order_tx"):
                        ord = tx.order_tx

                        # handle faucets
                        if ord.script == "FAUCET":
                            if ord.sender_address in faucets_in_this_block:
                                continue

                            # check if the account is empty
                            acc = current_state_copy.get_account(ord.sender_address)
                            if (
                                acc.micro_coins == 0
                                and acc.energy_wh == 0
                                and acc.nonce == 0
                            ):
                                txns_to_mine.append(tx)
                                faucets_in_this_block.add(ord.sender_address)
                                acc.micro_coins = 1
                            continue

                        # handle real trades
                        if active_grid_rate is None:
                            print(
                                f"[Miner] Skipping Trade {tx.transaction_hash[:16]}...: No active grid rate yet. Run 'post-quote' first!"
                            )
                            continue

                        # validate against working state
                        ctx = ValidationContext(
                            height=self.blockchain.get_tip().header.height + 1,
                            grid_rate=active_grid_rate,
                        )
                        ok, reason = validate_order_tx(tx, ctx, current_state_copy)

                        if ok:
                            # create TradeTx
                            trade_tx = create_trade_tx(
                                ord, active_grid_rate, self.address, fee=0
                            )
                            txns_to_mine.append(trade_tx)

                            # update working state (nonce + money) to prevent double-spending in same block
                            acc = current_state_copy.get_account(ord.sender_address)
                            acc.nonce = ord.nonce
                        else:
                            # order is invalid
                            print(
                                f"[Miner] Skipping Order {tx.transaction_hash[:16]}...: Validation Failed - {reason}"
                            )
                            continue

                # attempt to mine the block
                self.mining_interrupt.clear()
                tip = self.blockchain.get_tip()
                mined_block = None

                if len(txns_to_mine) > 0 or random.random() < 0.3:
                    print(
                        f"[Miner] Mining Block with {len(txns_to_mine)} transactions..."
                    )
                    mined_block = construct_and_mine_block(
                        tip, txns_to_mine, DIFFICULTY, stop_event=self.mining_interrupt
                    )

                if mined_block:
                    success = self.blockchain.add_block(mined_block)
                    print(f"Block {mined_block.header.height} Appended: {success}")
                    if success:
                        block_hash = calculate_header_hash(mined_block.header)
                        self.seen_blocks.add(block_hash)
                        print(
                            f"[IP: {self.address}] [Block Mined] Block Hash: {block_hash}"
                        )

                        # broadcast
                        thread = threading.Thread(
                            target=self.broadcast_block, args=(mined_block,)
                        )
                        thread.start()
                else:
                    if txns_to_mine:
                        print("Mining interrupted or failed")

            except Exception as e:
                print(f"[Miner] Error in mine_loop: {e}")

            time.sleep(random.randint(3, 5))

    def auto_faucet_loop(self):
        """Background thread that watches for any .json wallets and funds them if empty."""
        # tracking the addrs we have already submitted
        pending_faucets = set()

        while True:
            try:
                for filename in os.listdir("."):
                    if (
                        not filename.endswith(".json")
                        or filename == "grid_wallet.json"
                        or filename == "package.json"
                    ):
                        continue

                    with open(filename, "r") as f:
                        try:
                            data = json.load(f)
                        except:
                            continue

                        user_pub = data.get("public_key_hex")
                        user_priv = data.get("private_key_hex")

                        if user_pub and user_priv:
                            if user_pub in pending_faucets:
                                # check if it has actually been settled
                                account = self.blockchain.state.get_account(user_pub)
                                if account.micro_coins > 0:
                                    pending_faucets.remove(user_pub)
                                continue

                            # check if the account is empty
                            account = self.blockchain.state.get_account(user_pub)
                            if (
                                account.micro_coins == 0
                                and account.energy_wh == 0
                                and account.nonce == 0
                            ):
                                order = energy_chain_pb2.OrderTx()
                                order.sender_address = user_pub
                                order.type = energy_chain_pb2.PUSH
                                order.energy_wh = 1
                                order.limit_price = 1
                                order.nonce = 0
                                order.script = "FAUCET"

                                # sign and add to mempool
                                tx = energy_chain_pb2.Transaction()
                                tx.order_tx.CopyFrom(order)
                                sign_tx(tx, user_priv)
                                tx.transaction_hash = calculate_tx_hash(tx)

                                # add to mempool if not seen
                                if tx.transaction_hash not in self.seen_transactions:
                                    print(
                                        f"[IP: {self.address}] [Faucet] Found {filename}, requesting grant for {user_pub[:16]}..."
                                    )
                                    self.mempool.put(tx)
                                    self.seen_transactions.add(tx.transaction_hash)
                                    pending_faucets.add(user_pub)
                                    self.broadcast_transaction(tx)

            except Exception:
                pass
            time.sleep(5)

    def broadcast_transaction(self, tx_proto):
        print(
            f"[IP: {self.address}] [Broadcast] New Transaction Hash: {tx_proto.transaction_hash}"
        )
        for peer in self.known_peers:
            if peer != self.address:
                try:
                    channel = grpc.insecure_channel(f"{peer}:{PORT}")
                    stub = energy_chain_pb2_grpc.NodeServiceStub(channel)
                    stub.SubmitTx(tx_proto)
                except Exception as e:
                    print(f"Failed to broadcast tx to {peer}: {e}", file=sys.stderr)

    def broadcast_block(self, block_proto):
        for peer in self.known_peers:
            if peer != self.address:
                try:
                    channel = grpc.insecure_channel(f"{peer}:{PORT}")
                    stub = energy_chain_pb2_grpc.NodeServiceStub(channel)
                    stub.SubmitBlock(block_proto)
                except Exception as e:
                    print(f"Failed to broadcast block to {peer}: {e}", file=sys.stderr)

    def sync_chain(self, peer_addr):
        # fetch missing blocks from peer
        print(f"[IP: {self.address}] [Sync] Starting fetch from {peer_addr}...")
        try:
            channel = grpc.insecure_channel(f"{peer_addr}:{PORT}")
            stub = energy_chain_pb2_grpc.NodeServiceStub(channel)

            # ask for peer tip
            peer_tip = stub.GetTip(energy_chain_pb2.GetTipRequest())
            if peer_tip.header.height <= self.blockchain.get_tip().header.height:
                return

            # if they aren't longer, then get the full chain
            request = energy_chain_pb2.GetBlocksRequest(
                start_height=0, end_height=peer_tip.header.height
            )
            response = stub.GetBlocks(request)

            if self.blockchain.replace_chain(response.blocks):
                # interrupt mining to switch to the new tip
                self.mining_interrupt.set()
        except Exception as e:
            print(f"Sync failed from {peer_addr}: {e}", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise Exception("Incorrect arguments")

    ip_add = sys.argv[1]
    try:
        ip_add = socket.gethostbyname(ip_add)
    except Exception:
        pass

    node = Node(ip_add)
    node.run()
