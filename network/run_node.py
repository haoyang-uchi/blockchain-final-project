import os
import json
import grpc
import time
import sys
from concurrent import futures
import queue
import random
import threading
from network.node_service import NodeService
import network.config as config
import proto.energy_chain_pb2 as energy_chain_pb2
import proto.energy_chain_pb2_grpc as energy_chain_pb2_grpc
from core.blockchain import Blockchain
from core.miner import construct_and_mine_block

from core.wallet import Wallet
from core.cryptography import sign_tx
from core.block import calculate_tx_hash, calculate_header_hash

# Load values from config
PORT = config.PORT
DISCOVERY_TIMEOUT_SECS = config.DISCOVERY_TIMEOUT_SECS
DIFFICULTY = config.MINING_DIFFICULTY
MAX_TXN_PER_BLOCK = config.MAX_TXN_PER_BLOCK # TODO: maybe move this in blockchain class

"""Logical representation of the entire node. """
class Node():
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
        
        # Start the automatic faucet monitor
        threading.Thread(target=self.auto_faucet_loop, daemon=True).start()

    def run(self):
        """
        Function to run node. First registers node, second executes peer discovery, and finally starts mining / 
        listening for new nodes joining the network.  
        """
        registration_response = self.register()
        
        known_peers_arr = [registration_response.last_registered] if registration_response.last_registered else []
        print(f"[IP: {self.address}] [Registration] Response known peers: {known_peers_arr}")
        
        self.discovery(registration_response.last_registered) # Run discovery process
        
        print(f"[IP: {self.address}] Final known peers before mining: {self.known_peers}")
        
        self.listening_newnodes() # This times out after 10 seconds. Assumes all nodes join network in that time period.

        print(f"[IP: {self.address}] Node starts mining")
        miner = threading.Thread(target=self.mine_loop, args=())
        miner.start()
        # Run node for as long as the threads run - should only be stopped upon keyboard interrupt
        miner.join()

    def register(self):
        """
        Registers node with network by sending registration request to registrar node. Returns registration response
        from registrar.
        """
        print(f"[IP: {self.address}] Registering with DNS_SEED at address: dns_seed:{PORT}")
        channel = grpc.insecure_channel('dns_seed' + ":" + PORT)
        # channel = grpc.insecure_channel('localhost' + ":" + PORT)
        stub = energy_chain_pb2_grpc.RegisterStub(channel)
        response = stub.RegisterNode(energy_chain_pb2.RegistrationRequest(nVersion=1, nTime=time.time(), addrMe=self.address))
        return response

    def discovery(self, contact_node_addr: str):
        """
        Peer discovery of other nodes in the network. Initially, function is called with the node 
        that last registered with the registrar. Function is recursively called until there are no new 
        nodes to contact. 
        """
        # Base case: no node to contact
        if not contact_node_addr:
            return 

        # Contact node
        print(f"[IP: {self.address}] [Handshake] Peer IP: {contact_node_addr}")
        # Create channel to node trying to contact
        channel = grpc.insecure_channel(contact_node_addr+ ":" + PORT)
        handshake_stub = energy_chain_pb2_grpc.NodeServiceStub(channel)
        handshake_response = handshake_stub.GetPeers(energy_chain_pb2.GetPeersRequest(nVersion=1, nTime=time.time(), addrMe=self.address, bestHeight=0))
        
        self.known_peers.append(contact_node_addr)

        # Gossip approach - contact node's known peers
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
        energy_chain_pb2_grpc.add_NodeServiceServicer_to_server(NodeService(self), self.listener)
        self.listener.add_insecure_port(f"0.0.0.0:{PORT}")
        self.listener.start()
        time.sleep(DISCOVERY_TIMEOUT_SECS)


    def mine_loop(self):
        # Sleep initially to allow docker DNS to populate and node listeners to bind
        time.sleep(2)

        while True:
            try:
                # collect transactions
                txns_to_mine = []
                while len(txns_to_mine) < MAX_TXN_PER_BLOCK:
                    try:
                        tx = self.mempool.get(block=False)
                        
                        # Lazy Pruning: skip if already in chain
                        if any(b.has_transaction(tx.transaction_hash) for b in self.blockchain.chain):
                            continue

                        # Check nonce against state
                        sender = ""
                        is_faucet = False
                        if tx.HasField("order_tx"):
                            sender = tx.order_tx.sender_address
                            tx_nonce = tx.order_tx.nonce
                            is_faucet = (tx.order_tx.script == "FAUCET")
                        elif tx.HasField("grid_rate_tx"):
                            sender = tx.grid_rate_tx.grid_address
                            tx_nonce = 0 # TODO: Nonce for grid rate
                        
                        if sender:
                            account = self.blockchain.state.get_account(sender)
                            # Standard tx: must be > current nonce
                            # Faucet tx: nonce is 0, account.nonce is 0. allowed.
                            if not is_faucet and account.nonce >= tx_nonce and tx.HasField("order_tx"):
                                continue
                                
                        txns_to_mine.append(tx)
                    except queue.Empty:
                        break

                if len(txns_to_mine) > 0 or random.random() < 0.1: # Mine empty blocks sometimes
                    print(f"[Miner] Mining Block with {len(txns_to_mine)} transactions...")
                    self.mining_interrupt.clear()
                    tip = self.blockchain.get_tip()
                    mined_block = construct_and_mine_block(tip, txns_to_mine, DIFFICULTY, stop_event=self.mining_interrupt)
                if mined_block:
                    success = self.blockchain.add_block(mined_block)
                    print(f"Block {mined_block.header.height} Appended: {success}")
                    if success:
                        # mark as seen and broadcast
                        block_hash = calculate_header_hash(mined_block.header)
                        self.seen_blocks.add(block_hash)
                        
                        print(f"[IP: {self.address}] [Block Mined] Block Hash: {block_hash}")
                        
                        # broadcast to network
                        thread = threading.Thread(target=self.broadcast_block, args=(mined_block,))
                        thread.start()
                else:
                    print("Mining interrupted or failed")

            except KeyboardInterrupt:
                print("Shutting down mining upon keyboard interrupt")
                return
            # TODO: Broadcast the block has been mined / handle that across nodes

            # Upon finishing, sleep for random amount of time to avoid conflicts
            time.sleep(random.randint(3,5))

    def auto_faucet_loop(self):
        """Background thread that watches for any .json wallets and funds them if empty."""
        pending_faucets = set() # Track addresses we've already submitted for
        
        while True:
            try:
                for filename in os.listdir("."):
                    if not filename.endswith(".json") or filename == "grid_wallet.json" or filename == "package.json":
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
                                # Re-check if it actually settled
                                account = self.blockchain.state.get_account(user_pub)
                                if account.micro_coins > 0:
                                    pending_faucets.remove(user_pub)
                                continue

                            account = self.blockchain.state.get_account(user_pub)
                            if account.micro_coins == 0 and account.energy_wh == 0 and account.nonce == 0:
                                order = energy_chain_pb2.OrderTx()
                                order.sender_address = user_pub
                                order.type = energy_chain_pb2.PUSH
                                order.energy_wh = 1 
                                order.limit_price = 1
                                order.nonce = 0 
                                order.script = "FAUCET"
                                
                                tx = energy_chain_pb2.Transaction()
                                tx.order_tx.CopyFrom(order)
                                sign_tx(tx, user_priv)
                                tx.transaction_hash = calculate_tx_hash(tx)
                                
                                if tx.transaction_hash not in self.seen_transactions:
                                    print(f"[IP: {self.address}] [Faucet] Found {filename}, requesting grant for {user_pub[:16]}...")
                                    self.mempool.put(tx)
                                    self.seen_transactions.add(tx.transaction_hash)
                                    pending_faucets.add(user_pub)
                                    self.broadcast_transaction(tx)
                                    
            except Exception:
                pass
            time.sleep(5)

    def broadcast_transaction(self, tx_proto):
        print(f"[IP: {self.address}] [Broadcast] New Transaction Hash: {tx_proto.transaction_hash}")
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

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise Exception("Incorrect arguments")

    ip_add = sys.argv[1]
    import socket
    try:
        ip_add = socket.gethostbyname(ip_add)
    except Exception:
        pass

    node = Node(ip_add) # Pass in address of docker container
    node.run()
        