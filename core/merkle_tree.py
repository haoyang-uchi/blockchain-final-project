# core/merkle_tree.py

import hashlib

class MerkleTree:
    def __init__(self, tx_hashes):
        self.tx_hashes = tx_hashes
        self.layers = [tx_hashes]
        self.root = ""

    def find_root(self):
        tx_bytes = []
        for hash in self.tx_hashes:
            tx_bytes.append(bytes.fromhex(hash))

        root_bytes = self.process(tx_bytes)
        self.root = root_bytes.hex()
        return self.root

    # digest after hashing twice
    def double_sha256(self, bytes):
        return hashlib.sha256(hashlib.sha256(bytes).digest()).digest()

    # recursively finds the root
    def process(self, hash_bytes):
        # base case
        if len(hash_bytes) == 1:
            return hash_bytes[0]

        # add duplicate if odd
        if len(hash_bytes) % 2 == 1:
            hash_bytes.append(hash_bytes[-1])

        new_tx_bytes = []
        current_layer = []

        # pair hashes, double hash, add to array
        for i in range(0, len(hash_bytes), 2):
            combined_bytes = hash_bytes[i] + hash_bytes[i + 1]
            sha2_bytes = self.double_sha256(combined_bytes)
            new_tx_bytes.append(sha2_bytes)
            current_layer.append(sha2_bytes.hex())

        self.layers.append(current_layer)
        return self.process(new_tx_bytes)
