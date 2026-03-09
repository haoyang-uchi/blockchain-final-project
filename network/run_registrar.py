import os
import sys

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root)

import grpc
import configparser
from concurrent import futures
import logging
import sys
import os
import proto.energy_chain_pb2 as energy_chain_pb2
import proto.energy_chain_pb2_grpc as energy_chain_pb2_grpc

# Get port from config
PORT = "58333"

# Python class for register service + register node
class Registrar(energy_chain_pb2_grpc.RegisterServicer):
    def __init__(self):
        self.last_registered = None
        self.node_dict = {}

    def RegisterNode(self, request, context):
        known_peers_list = list(self.node_dict.keys())
        
        if not (request.addrMe in self.node_dict.keys()):
            self.last_registered = request.addrMe
            self.node_dict[request.addrMe] = {
                "nVersion":request.nVersion,
                "nTime":request.nTime,
            }
            print(f"[Network] Request from: {request.addrMe}")
            return energy_chain_pb2.RegistrationReply(success=True, last_registered=known_peers_list[-1] if known_peers_list else "")
        else: #TODO: case already registered - may change
            return energy_chain_pb2.RegistrationReply(success=False, last_registered=known_peers_list[-1] if known_peers_list else "")

def serve():
    port = PORT
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    energy_chain_pb2_grpc.add_RegisterServicer_to_server(Registrar(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print(f"DNS_SEED server started, port: {port}")
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    serve()
