# core/blockchain.py

from core.block import create_new_block, calculate_header_hash
from core.state import State, GRID_ADDRESS
import proto.energy_chain_pb2 as pb2
from typing import List


class Blockchain:
    def __init__(self):
        self.blocks: List[pb2.Block] = []
        self.state = State()
        self.initialize_genesis()

    def initialize_genesis(self):
        genesis = create_new_block(prev_hash="0" * 64, height=0, bits=0x1E0FFFF0)

        # giving the GRID a massive reserve
        # 100 GWh and 1 trillion Microcoins
        self.state.get_account(GRID_ADDRESS).energy_wh = 100_000_000_000
        self.state.get_account(GRID_ADDRESS).coins_micro = 1_000_000_000_000

        # testing accounts
        # REMOVE LATER
        test_user_a = "userA"
        self.state.update_account(test_user_a, energy_delta=5000, coins_delta=100_000)

        test_user_b = "userB"
        self.state.update_account(test_user_b, energy_delta=0, coins_delta=5_000_000)

        self.blocks.append(genesis)
        print("Created Genesis Block")

    # adds a block to the chain
    def add_block(self, block: pb2.Block) -> bool:
        tip = self.get_tip()
        if block.header.height != tip.header.height + 1:
            print(
                f"Block height {block.header.height} invalid. Expected {tip.header.height + 1}"
            )
            return False

        if block.header.hash_prev_block != calculate_header_hash(tip.header):
            print("Block prev_hash does not match local tip hash.")
            return False

        self.blocks.append(block)
        print(f"Appended Block Height {block.header.height} to Chain")
        return True

    def get_tip(self) -> pb2.Block:
        return self.blocks[-1]

    def get_block_by_height(self, height: int) -> pb2.Block:
        if 0 <= height < len(self.blocks):
            return self.blocks[height]
        return None
