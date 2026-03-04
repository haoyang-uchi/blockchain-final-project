# core/miner.py

import time
from core.block import Block
from core.blockchain import Blockchain
from core.output import Output
from core.transaction import Transaction
from core.txn_memory_pool import TxnMemoryPool


class Miner:
    def __init__(self):
        self.cryptocurrency_name = "PolyGlass"
        self.max_txns = Block.MAX_TXNS  # 10

    def target(self, bits):
        # shifting to get the leading 2 hex
        exponent_hex = bits >> 24
        exponent = int(exponent_hex & 0xFF)
        coefficient = bits & 0xFFFFFF
        target = coefficient * (2 ** (8 * (exponent - 3)))
        return target

    def generate_coinbase_txn(self):
        inputs = ["polyglass_coinbase_txn_" + str(int(time.time()))]
        output = Output(100000, "POLYGLASS SCRIPT")
        return Transaction(inputs, [output])

    def mine(self, blockchain: Blockchain, memory: TxnMemoryPool):
        # get memory transactions and create coinbase transaction
        memory_txns = memory.get_transactions(self.max_txns - 1)
        coinbase_txn = self.generate_coinbase_txn()
        transactions = [coinbase_txn] + memory_txns

        # candidate block
        prev_hash = "0" * 64
        if blockchain.blockchain:
            prev_hash = blockchain.blockchain[-1].block_hash
        block = Block(prev_hash)
        for txn in transactions:
            block.add_transaction(txn)

        # lab default is 0x207fffff
        block.block_header.bits = 0x207FFFFF
        target = self.target(block.block_header.bits)

        print("Mining Block...")
        print(f"Number of Transactions: {len(transactions)}")
        print(f"Target: {target}")

        # start proof of work
        self.proof_of_work(block, 0, target)

        # add block to blockchain
        blockchain.add_block(block)

        return block

    def proof_of_work(self, block: Block, nonce: int, target: int):
        while True:
            block.block_header.nonce = nonce
            block.block_header.timestamp = int(time.time())

            block_hex_hash = block.calculate_block_hash(block.block_header)
            block_int_hash = int(block_hex_hash, 16)

            if block_int_hash < target:
                block.block_hash = block_hex_hash
                print("Block mining complete!")
                print(f"Block hash: {block.block_hash}")
                print(f"Nonce: {nonce}")
                break

            nonce += 1
            if nonce % 1000000 == 0:
                print(f"Continuing mining - Current nonce: {nonce}")
