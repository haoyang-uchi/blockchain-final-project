# core/blockchain.py

from core.block import create_new_block, calculate_header_hash
from core.state import State, GRID_ADDRESS
from core.miner import verify
from state.execution import apply_block
import proto.energy_chain_pb2 as pb2
from typing import List


class Blockchain:
    def __init__(self):
        self.blocks: List[pb2.Block] = []
        self.state = State()
        self.initialize_genesis()

    def initialize_genesis(self):
        genesis = create_new_block(prev_hash="0" * 64, height=0, bits=0x1E0FFFF0)

        # giving the grid 100 GWh (which is a lot)
        self.state.get_account(GRID_ADDRESS).energy_wh = 100_000_000_000
        # giving 1 trillion microcoins
        self.state.get_account(GRID_ADDRESS).micro_coins = 1_000_000_000_000

        self.blocks.append(genesis)
        print("Created Genesis Block")

    # adds a block to the chain
    def add_block(self, block: pb2.Block) -> bool:
        tip = self.get_tip()
        if block.header.height <= tip.header.height:
            return False
            
        if block.header.height != tip.header.height + 1:
            print(
                f"Block height {block.header.height} invalid. Expected {tip.header.height + 1}"
            )
            return False

        if block.header.hash_prev_block != calculate_header_hash(tip.header):
            print("Block prev_hash does not match local tip hash.")
            return False
            
        if not verify(block.header):
            print("Block proof of work is invalid.")
            return False
        
        new_state, success, reason = apply_block(block, self.state)
        if not success:
            print(f"Block state execution failed: {reason}")
            return False

        self.state = new_state
        self.blocks.append(block)
        print(f"Appended Block Height {block.header.height} to Chain")
        return True

    # gets the tip of the chain
    def get_tip(self) -> pb2.Block:
        return self.blocks[-1]

    # gets a block by height
    def get_block_by_height(self, height: int) -> pb2.Block:
        if 0 <= height < len(self.blocks):
            return self.blocks[height]
        return None

    # validates a chain and replaces the local one if it's invalid
    def replace_chain(self, new_blocks: List[pb2.Block]) -> bool:
        if len(new_blocks) <= len(self.blocks):
            return False
            
        print(f"Trying chain replacement: local={len(self.blocks)}, remote={len(new_blocks)}")
        
        # start from a fresh state
        temp_state = State()
        temp_state.get_account(GRID_ADDRESS).energy_wh = 100_000_000_000
        temp_state.get_account(GRID_ADDRESS).micro_coins = 1_000_000_000_000

        # verify blocks from the genesis block
        for i, block in enumerate(new_blocks):
            if i == 0:
                # genesis block check
                if block.header.height != 0:
                    return False
                continue

            # check height and previous hash
            if block.header.height != i:
                return False
            if block.header.hash_prev_block != calculate_header_hash(new_blocks[i-1].header):
                return False
            
            # check proof of work
            if not verify(block.header):
                return False
                
            new_state, success, reason = apply_block(block, temp_state)
            if not success:
                print(f"Reorg failed at height {i}: {reason}")
                return False
            temp_state = new_state
            
        self.blocks = list(new_blocks)
        self.state = temp_state
        print(f"Chain Replaced! New height: {len(self.blocks) - 1}")
        return True
