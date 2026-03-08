import grpc
import time
import sys
from concurrent import futures
from node_service import NodeService
import os
import config

sys.path.append(os.path.abspath("../proto")) # TODO: find a better way to import
import energy_chain_pb2, energy_chain_pb2_grpc

# Get port (probably 50051) from config
PORT = config.PORT

"""Logical representation of the entire node. """
class Node():
    def __init__(self, my_address):
        """
        Given a the docker address of the docker container the code runs in initializes a node.
        """
        self.address = my_address
        self.known_peers = []

    def run(self):
        """
        Function to run node. First registers node, second executes peer discovery, and finally starts mining / 
        listening for new nodes joining the network.  
        """
        registration_response = self.register()
        self.discovery(registration_response.last_registered) # Run discovery process
        self.listening() # TODO: this will be a thread listening for incoming connections on server
        # TODO: Mining

    def register(self):
        """
        Registers node with network by sending registration request to registrar node. Returns registration response
        from registrar.
        """
        channel = grpc.insecure_channel('grpc_server' + ":" + PORT)
        stub = energy_chain_pb2_grpc.RegisterStub(channel)
        response = stub.SendRegistration(energy_chain_pb2.RegistrationRequest(nVersion=1, nTime=time.time(), addrMe=self.address))
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
        handshake_stub = energy_chain_pb2_grpc.HandshakeStub(channel)
        handshake_response = handshake_stub.SendHandshakeReply(energy_chain_pb2.HandshakeRequest(nVersion=1, nTime=time.time(), addrMe=self.address, bestHeight=0))
        if not handshake_response.success: # TODO: Probably a better way to raise errors. 
            raise Exception(f"Error with handshake from {self.address} to {contact_node_addr}")
        self.known_peers.append(contact_node_addr)
        print(f"Successful handshake {self.address} to {contact_node_addr}")

        # Gossip approach - contact node's known peers
        if len(handshake_response.knownPeers) == 0:
            print(f"No more peers to discover")
            self.discovery(None)
        else:
            print(f"Exploring peers: {handshake_response.knownPeers}")
            for peer_addr in handshake_response.knownPeers:
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
        listener.wait_for_termination()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise Exception("Incorrect arguments")

    node = Node(sys.argv[1]) # Pass in address of docker container
    node.run()
        