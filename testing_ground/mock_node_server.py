import os
import sys

# Add project root to sys.path
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root)

import grpc
from concurrent import futures

import proto.energy_chain_pb2 as pb2
import proto.energy_chain_pb2_grpc as pb2_grpc


class MockNodeService(pb2_grpc.NodeServiceServicer):
    def SubmitTx(self, request, context):
        print("SubmitTx received")
        print(f"tx_hash={request.transaction_hash}")
        return pb2.SubmitResponse(success=True, message="mock accepted")

    def GetTip(self, request, context):
        block = pb2.Block()
        block.header.version = 1
        block.header.height = 42
        block.header.hash_prev_block = "00" * 32
        return block

    def SubmitBlock(self, request, context):
        return pb2.SubmitResponse(success=True, message="mock block accepted")

    def GetBlocks(self, request, context):
        return pb2.GetBlocksResponse(blocks=[])

    def GetPeers(self, request, context):
        return pb2.GetPeersResponse(peer_addresses=[])


def main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    pb2_grpc.add_NodeServiceServicer_to_server(MockNodeService(), server)
    server.add_insecure_port("127.0.0.1:50051")
    server.start()
    print("Mock server listening on 127.0.0.1:50051")
    server.wait_for_termination()


if __name__ == "__main__":
    main()
