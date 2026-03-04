# core/txn_memory_pool.py

from core.transaction import Transaction
from typing import List


class TxnMemoryPool:
    def __init__(self):
        self.transactions: List[Transaction] = []

    def add_transaction(self, transaction: Transaction):
        self.transactions.append(transaction)

    def get_transactions(self, txn_count: int) -> List[Transaction]:
        if txn_count > len(self.transactions):
            txn_count = len(self.transactions)
        transactions = self.transactions[:txn_count]
        self.transactions = self.transactions[txn_count:]
        return transactions

    def is_empty(self):
        return len(self.transactions) == 0
