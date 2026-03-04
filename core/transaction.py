# core/transaction.py

from typing import List
from core.output import Output
import hashlib


class Transaction:
    def __init__(self, list_of_inputs: List[str], list_of_outputs: List[Output]):
        self.version_number = 1
        self.in_counter = len(list_of_inputs)
        self.list_of_inputs = list_of_inputs
        self.out_counter = len(list_of_outputs)
        self.list_of_outputs = list_of_outputs
        self.transaction_hash = self.calculate_transaction_hash()

    def calculate_transaction_hash(self):
        output_str = ""
        for output in self.list_of_outputs:
            output_str += str(output.value) + output.script

        combined_string = (
            str(self.version_number)
            + str(self.in_counter)
            + "".join(self.list_of_inputs)
            + str(self.out_counter)
            + output_str
        )
        hash_bytes = combined_string.encode("utf-8")
        return hashlib.sha256(hashlib.sha256(hash_bytes).digest()).hexdigest()

    def printTransaction(self):
        print("\nTransaction Information")
        print("-" * 70)
        print(f"Version Number: {self.version_number}")
        print(f"Input Counter: {self.in_counter}")
        print(f"List of Inputs: {self.list_of_inputs}")
        print(f"Output Counter: {self.out_counter}")
        print(f"List of Outputs:")
        for output in self.list_of_outputs:
            print(f"Value (Shards): {output.value}, Script: {output.script}")
        print(f"Transaction Hash: {self.transaction_hash}")
        print("-" * 70)
