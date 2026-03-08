import grpc
import time
import sys
from concurrent import futures
import queue
import random
from net.node_service import NodeService
import net.config as config
import proto.energy_chain_pb2 as energy_chain_pb2
import proto.energy_chain_pb2_grpc as energy_chain_pb2_grpc
from core.blockchain import Blockchain

# TODO: the following imports will not be necessary after CLI sends txns
from core.cryptography import generate_key, sign_tx
from core.block import calculate_tx_hash

# Get port (probably 50051) from config
PORT = config.PORT
DISCOVERY_TIMEOUT_SECS = config.DISCOVERY_TIMEOUT_SECS

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

    def run(self):
        """
        Function to run node. First registers node, second executes peer discovery, and finally starts mining / 
        listening for new nodes joining the network.  
        """
        registration_response = self.register()
        self.discovery(registration_response.last_registered) # Run discovery process
        self.listening() # This times out after 5 seconds. Assumes all nodes join network in that time period.
        print(f"Node with address {self.address} starts mining")
        # TODO: Mining
        # TXN discoverer (adds txns to mempool every 2 to 5 secs)
        # Miner 
            # sleeps for some time, starts mining from queue

    # TODO: will be deleted once CLI working
    def generate_mock_tx(self, priv_key, pub_key, push_rate, pull_rate):
        """From tests directory."""
        grid_rate = energy_chain_pb2.GridRateTx()
        grid_rate.push_rate = push_rate
        grid_rate.pull_rate = pull_rate
        grid_rate.expiry_height = 100
        grid_rate.grid_address = pub_key

        tx = energy_chain_pb2.Transaction()
        tx.grid_rate_tx.CopyFrom(grid_rate)
        sign_tx(tx, priv_key)
        tx.transaction_hash = calculate_tx_hash(tx)
        return tx

    def discover_txns(self):
        """For now generates a bunch of transactions and adds to mempool."""
        priv, pub = generate_key()

        # Generate a lot of initial transactions
        for _ in range(100):
            txn = self.generate_mock_tx(priv, pub, 5, 12)
            self.mempool.put(txn)

        while True:
            try: 
                txn = self.generate_mock_tx(priv, pub, 5, 12)
                self.mempool.put(txn)
                time.sleep(random.randint(2,5))
            except KeyboardInterrupt:
                return

    def mine_loop(self):
        pass

    def register(self):
        """
        Registers node with network by sending registration request to registrar node. Returns registration response
        from registrar.
        """
        channel = grpc.insecure_channel('grpc_server' + ":" + PORT)
        stub = energy_chain_pb2_grpc.RegisterStub(channel)
        response = stub.RegisterNode(energy_chain_pb2.RegistrationRequest(nVersion=1, nTime=time.time(), addrMe=self.address))
        print(f"Greeter client received: {response.last_registered}")
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
        print(f"Attempting handshake {self.address} to {contact_node_addr}")
        # Create channel to node trying to contact
        channel = grpc.insecure_channel(contact_node_addr+ ":" + PORT)
        handshake_stub = energy_chain_pb2_grpc.NodeServiceStub(channel)
        handshake_response = handshake_stub.GetPeers(energy_chain_pb2.GetPeersRequest(nVersion=1, nTime=time.time(), addrMe=self.address, bestHeight=0))
        
        self.known_peers.append(contact_node_addr)
        print(f"Successful handshake {self.address} to {contact_node_addr}")

        # Gossip approach - contact node's known peers
        if len(handshake_response.peer_addresses) == 0:
            print(f"No more peers to discover")
            self.discovery(None)
        else:
            print(f"Exploring peers: {handshake_response.peer_addresses}")
            for peer_addr in handshake_response.peer_addresses:
                if peer_addr != self.address and (not peer_addr in self.known_peers):
                    self.discovery(peer_addr)

    def listening(self):
        """
        Function to listen for new nodes joining the network. Upon a GetPeersRequest (contact by new node), 
        adds new node to list of known peers and sends response of list of known peers. 
        """
        print(f"Launching node server for {self.address}")
        listener = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        energy_chain_pb2_grpc.add_NodeServiceServicer_to_server(NodeService(self), listener)
        listener.add_insecure_port(f"{self.address}:{PORT}")
        listener.start()
        print("Node server started, listening on " + f"{self.address}:{PORT}")
        listener.wait_for_termination(timeout=DISCOVERY_TIMEOUT_SECS)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise Exception("Incorrect arguments")

    ip_add = sys.argv[1]
    node = Node(ip_add) # Pass in address of docker container
    node.run()
        