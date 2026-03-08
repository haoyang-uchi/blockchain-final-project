import configparser
import grpc
from concurrent import futures
import logging
import sys
import os
import config

sys.path.append(os.path.abspath("../proto")) # TODO: find a better way to import
import energy_chain_pb2, energy_chain_pb2_grpc

# Get port from config
PORT = config.PORT

# Python class for register service + register node
class Registrar(energy_chain_pb2_grpc.RegisterServicer):
    def __init__(self):
        self.last_registered = None
        self.node_dict = {}

    def RegisterNode(self, request, context):
        last_registered = self.last_registered
        if not (request.addrMe in self.node_dict.keys()):
            self.last_registered = request.addrMe
            self.node_dict[request.addrMe] = {
                "nVersion":request.nVersion,
                "nTime":request.nTime,
            }
            return energy_chain_pb2.RegistrationReply(success=True, last_registered=last_registered)
        else: #TODO: case already registered - may change
            return energy_chain_pb2.RegistrationReply(success=False, last_registered=last_registered)

def serve():
    port = PORT
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    energy_chain_pb2_grpc.add_RegisterServicer_to_server(Registrar(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    serve()
