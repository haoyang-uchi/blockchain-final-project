# core/block.py

import time
import hashlib
import proto.energy_chain_pb2 as pb2
from core.merkle_tree import MerkleTree
from typing import List


# serializes the proto header and then does a double SHA-256
def calculate_header_hash(header: pb2.Header):
    header_bytes = header.SerializeToString()
    return hashlib.sha256(hashlib.sha256(header_bytes).digest()).hexdigest()


# calculates the merkle
def get_merkle_root(transactions: List[pb2.Transaction]):
    tx_hashes = []
    for tx in transactions:
        tx_hashes.append(tx.transaction_hash)

    if not tx_hashes:
        return ""

    mt = MerkleTree(tx_hashes)
    return mt.find_root()


# calculates hash of a proto transaction
def calculate_tx_hash(tx: pb2.Transaction) -> str:
    # create a copy of the transaction to prevent changes
    tmp_tx = pb2.Transaction()
    tmp_tx.CopyFrom(tx)
    tmp_tx.transaction_hash = ""
    tx_bytes = tmp_tx.SerializeToString()
    return hashlib.sha256(hashlib.sha256(tx_bytes).digest()).hexdigest()


# creates a new block (mapped to the proto block def)
def create_new_block(prev_hash: str, height: int, bits: int) -> pb2.Block:
    block = pb2.Block()
    block.header.version = 1
    block.header.hash_prev_block = prev_hash
    block.header.timestamp = int(time.time())
    block.header.bits = bits
    block.header.nonce = 0
    block.header.height = height
    return block
