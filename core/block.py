# core/block.py

import time
import hashlib
import proto.energy_chain_pb2 as pb2
from core.header import Header
from core.merkle_tree import MerkleTree
from core.transaction import Transaction
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
        return  ""

    mt = MerkleTree(tx_hashes)
    return mt.find_root()
