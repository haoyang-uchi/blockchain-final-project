from concurrent import futures
import sys
import os
import proto.energy_chain_pb2 as energy_chain_pb2
import proto.energy_chain_pb2_grpc as energy_chain_pb2_grpc
from core.block import calculate_tx_hash, calculate_header_hash
import threading

class NodeService(energy_chain_pb2_grpc.NodeServiceServicer):
    def __init__(self, host_node):
        self.host_node = host_node # Node python object belonging to node providing service

    def GetPeers(self, request, context):
        print(f"[IP: {self.host_node.address}] [Handshake Received] From: {request.addrMe}, Height: {request.bestHeight}")
        if not request.addrMe in self.host_node.known_peers:
            print(f"Request address not in known peers: {request.addrMe}")
            (self.host_node.known_peers).append(request.addrMe)
            print(f"[IP: {self.host_node.address}] Added {request.addrMe} to known peers via handshake")
        return energy_chain_pb2.GetPeersResponse(peer_addresses=self.host_node.known_peers)

    def SubmitTx(self, request, context):
        tx_hash = request.transaction_hash
        if tx_hash not in self.host_node.seen_transactions:
            self.host_node.seen_transactions.add(tx_hash)
            
            print(f"[IP: {self.host_node.address}] [Seen] New Transaction Hash: {tx_hash}")
            self.host_node.mempool.put(request)
            
            # gossip
            thread = threading.Thread(
                target=self.host_node.broadcast_transaction, args=(request,)
            )
            thread.start()
            
        return energy_chain_pb2.SubmitResponse(success=True, message="Transaction received")

    def SubmitBlock(self, request, context):
        block_hash = calculate_header_hash(request.header)
        if block_hash not in self.host_node.seen_blocks:
            self.host_node.seen_blocks.add(block_hash)
            
            print(f"[IP: {self.host_node.address}] [Broadcast] New Block Hash: {block_hash}")
            success = self.host_node.blockchain.add_block(request)
            
            if success:
                self.host_node.mining_interrupt.set()
                print(f"[IP: {self.host_node.address}] [Block Added] Adding Block Height {request.header.height} to chain")
                # gossip
                thread = threading.Thread(target=self.host_node.broadcast_block, args=(request,))
                thread.start()
            else:
                print(f"[IP: {self.host_node.address}] [Broadcast Rejected] Block Height {request.header.height} Invalid")
                
        return energy_chain_pb2.SubmitResponse(success=True, message="Block received")

    def GetTip(self, request, context):
        tip_block = self.host_node.blockchain.get_tip()
        return tip_block
    def GetAccount(self, request, context):
        account = self.host_node.blockchain.state.get_account(request.address)
        return energy_chain_pb2.AccountResponse(
            address=request.address,
            energy_wh=account.energy_wh,
            micro_coins=account.micro_coins,
            nonce=account.nonce
        )
