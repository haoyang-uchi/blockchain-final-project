# core/blockchain.py

from core.block import Block


class Blockchain:
    def __init__(self):
        self.blockchain = []
        self.create_genesis_block()
        self.genesis_block_hash = ""

    def add_block(self, block: Block):
        self.blockchain.append(block)

    def get_block(self, value: any):
        # height
        if isinstance(value, int) and 0 <= value < len(self.blockchain):
            return self.blockchain[value]
        # hash
        elif isinstance(value, str):
            for block in self.blockchain:
                if block.block_hash == value:
                    return block
        return None

    def get_transaction(self, transaction_hash: str):
        for block in self.blockchain:
            for transaction in block.transactions:
                if transaction.transaction_hash == transaction_hash:
                    return transaction
        return None

    def create_genesis_block(self):
        genesis_block = Block(0 * 64)
        # lab default is 0x207fffff
        genesis_block.bits = 0x207FFFFF
        genesis_block.block_hash = genesis_block.calculate_block_hash(
            genesis_block.block_header
        )
        self.add_block(genesis_block)
        self.genesis_block_hash = genesis_block.block_hash
        print(f"Genesis Block Hash: {genesis_block.block_hash}")
