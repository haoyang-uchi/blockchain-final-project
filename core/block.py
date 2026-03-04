# core/block.py

import time
import hashlib
from core.header import Header
from core.merkle_tree import MerkleTree
from core.transaction import Transaction


class Block:
    # max transactions constant
    MAX_TXNS = 10

    def __init__(self, previous_hash):
        self.magic_number = 0xD9B4BEF9
        self.block_size = 0
        self.transaction_counter = 0
        self.transactions = []
        self.block_hash = ""

        # block header
        self.block_header = Header()
        self.block_header.version = 1
        self.block_header.hash_prev_block = previous_hash
        self.block_header.timestamp = int(time.time())
        self.block_header.bits = 0
        self.block_header.nonce = 0

    # calculates the block hash
    def calculate_block_hash(self, block_header: Header):
        block_str = (
            str(block_header.timestamp)
            + str(block_header.hash_merkle_root)
            + str(block_header.bits)
            + str(block_header.nonce)
            + str(block_header.hash_prev_block)
        )
        block_bytes = block_str.encode("utf-8")
        return hashlib.sha256(hashlib.sha256(block_bytes).digest()).hexdigest()

    # add transaction to block
    def add_transaction(self, transaction: Transaction):
        self.transactions.append(transaction)
        self.update_merkle_tree()
        self.transaction_counter += 1

    # update the merkle tree root
    def update_merkle_tree(self):
        tx_hashes = []
        for tx in self.transactions:
            tx_hashes.append(tx.transaction_hash)

        if not tx_hashes:
            self.block_header.hash_merkle_root = ""
            return

        mt = MerkleTree(tx_hashes)
        self.block_header.hash_merkle_root = mt.find_root()

    def printBlock(self):
        print("\nBlock Information")
        print("-" * 70)
        print(f"Block Hash: {self.block_hash}")
        print(f"Magic Number: {self.magic_number}")
        print(f"Block Size: {self.block_size}")
        print(f"Transaction Counter: {self.transaction_counter}")
        print(f"\n---------- Transactions ----------")
        for tx in self.transactions:
            print(f"Transaction Hash: {tx.transaction_hash}")
        print("\n---------- Block Header ----------")
        print(f"Version: {self.block_header.version}")
        print(f"Previous Block Hash: {self.block_header.hash_prev_block}")
        print(f"Timestamp: {self.block_header.timestamp}")
        print(f"Bits: {self.block_header.bits}")
        print(f"Nonce: {self.block_header.nonce}")
        print(f"Merkle Root: {self.block_header.hash_merkle_root}")
        print("-" * 70)
