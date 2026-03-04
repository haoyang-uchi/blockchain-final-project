# main.py

import random
import time
from threading import Thread, Event
from core.blockchain import Blockchain
from core.block import Block
from core.miner import Miner
from core.output import Output
from core.transaction import Transaction
from core.txn_memory_pool import TxnMemoryPool

THREADING_ENABLED = False


def simulate_network(memory: TxnMemoryPool, blockchain: Blockchain, miner: Miner):
    stop_event = Event()
    thread = Thread(target=generate_network_transactions, args=(memory, stop_event))
    thread.start()
    print("\n---------- Started Network ----------")

    block_count = 0
    max_blocks = 10
    try:
        while block_count < max_blocks:
            # waiting for a transaction
            if memory.is_empty():
                print("Waiting for transactions from network...")
                time.sleep(5)
                continue

            print(f"\n---------- Mining Block {block_count + 1} ----------")
            miner.mine(blockchain, memory)
            block_count += 1
    finally:
        print("---------- Network Stopped ----------")
        stop_event.set()
        thread.join()


# generates transactions for threading
def generate_network_transactions(memory: TxnMemoryPool, stop_event: Event):
    while not stop_event.is_set():
        # 10 seconds is slow so I am doing between 1 and 5 seconds
        sleep_time = random.uniform(1, 5)
        time.sleep(sleep_time)

        # create transaction
        random_num = random.randint(1, 100000)
        inputs = [f"input_{random_num}"]
        value = random.randint(100, 10000)
        tx = Transaction(inputs, [Output(value, f"TXN_SCRIPT_{random_num}")])
        memory.add_transaction(tx)
        print(f"[NETWORK SIM] Received new transaction: {tx.transaction_hash}")


# generates a set count of transactions
def generate_transactions(memory: TxnMemoryPool, count: int):
    for i in range(count):
        random_num = random.randint(1, 100000)
        inputs = [f"input_{random_num}"]
        value = random.randint(100, 10000)  # 0.1 to 10 PolyGlass coins
        tx = Transaction(inputs, [Output(value, f"TXN_SCRIPT_{random_num}")])
        memory.add_transaction(tx)


def main():
    print("\nBlockchain Setup")
    print("-" * 70)

    # create blockchain
    blockchain = Blockchain()

    # create memory pool
    memory = TxnMemoryPool()

    # create miner
    miner = Miner()

    if THREADING_ENABLED:
        simulate_network(memory, blockchain, miner)
    else:
        # not sure if it was a typo but lab said 91 transactions
        generate_transactions(memory, 91)
        block_count = 0
        while not memory.is_empty():
            print(f"\n---------- Mining Block {block_count + 1} ----------")
            miner.mine(blockchain, memory)
            block_count += 1

    print("-" * 70)
    print("\n---------- Final Block ----------")
    final_block = blockchain.blockchain[-1]
    final_block.printBlock()
    print("\n---------- Results ----------")
    print(f"Total blocks: {len(blockchain.blockchain)}")
    print(f"Blockchain tip height: {len(blockchain.blockchain) - 1}")


if __name__ == "__main__":
    main()
