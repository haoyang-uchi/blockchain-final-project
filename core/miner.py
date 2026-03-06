# core/miner.py

import time
import proto.energy_chain_pb2 as pb2
from core.block import calculate_header_hash, get_merkle_root
from typing import List


def calculate_target(bits: int) -> int:
    # shifting to get the leading 2 hex
    exponent_hex = bits >> 24
    exponent = int(exponent_hex & 0xFF)
    coefficient = bits & 0xFFFFFF
    target_val = coefficient * (2 ** (8 * (exponent - 3)))
    return target_val


# verifies that double SHA-256 meets difficulty (proof of work)
def verify(header: pb2.Header) -> bool:
    block_hash = calculate_header_hash(header)
    hash_int = int(block_hash, 16)
    target_val = calculate_target(header.bits)
    return hash_int <= target_val


# mine a block
def mine_block(header: pb2.Header, max_nonce: int = 10_000_000) -> bool:
    # get the target
    target_val = calculate_target(header.bits)
    start_time = time.time()

    # keep checking proof of work until it hits
    for _ in range(max_nonce):
        if verify(header):
            elapsed = time.time() - start_time
            return True
        header.nonce += 1


# given the prev block and a list of tx, finds the merkle root, creates a
# new block header, and then mines the block
def construct_and_mine_block(
    prev_block: pb2.Block,
    transactions: List[pb2.Transaction],
    difficulty_bits: int = 0x207FFFFF,
) -> pb2.Block:
    new_block = pb2.Block()
    new_block.header.version = 1
    new_block.header.hash_prev_block = calculate_header_hash(prev_block.header)
    new_block.header.timestamp = int(time.time())
    new_block.header.bits = difficulty_bits
    new_block.header.nonce = 0
    new_block.header.height = prev_block.header.height + 1

    new_block.transactions.extend(transactions)
    new_block.header.hash_merkle_root = get_merkle_root(list(new_block.transactions))

    if mine_block(new_block.header):
        return new_block
    return None
