# core/header.py


class Header:
    def __init__(self):
        self.version = 1
        self.hash_prev_block = ""
        self.hash_merkle_root = ""
        self.timestamp = 0
        self.bits = 0
        self.nonce = 0
