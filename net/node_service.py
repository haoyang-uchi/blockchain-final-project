import grpc
from concurrent import futures
import time

from proto import energy_chain_pb2, energy_chain_pb2_grpc

class NodeService(energy_chain_pb2_grpc.NodeServiceServicer):
    def __init__(self, host_node):
        self.host_node = host_node # Node python object belonging to node providing service

    def GetPeers(self, request, context):
        # TODO: process request
        return energy_chain_pb2.GetPeersResponse(peer_addresses=self.host_node.known_peers) # TODO: implement node class
