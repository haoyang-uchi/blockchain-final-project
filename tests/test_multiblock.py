# tests/test_multiblock.py

from core.blockchain import Blockchain
from core.block import calculate_tx_hash
from core.miner import construct_and_mine_block
from core.cryptography import generate_key, sign_tx
import proto.energy_chain_pb2 as pb2


def generate_mock_tx(priv_key, pub_key, push_rate, pull_rate):
    grid_rate = pb2.GridRateTx()
    grid_rate.push_rate = push_rate
    grid_rate.pull_rate = pull_rate
    grid_rate.expiry_height = 100
    grid_rate.grid_address = pub_key

    tx = pb2.Transaction()
    tx.grid_rate_tx.CopyFrom(grid_rate)
    sign_tx(tx, priv_key)
    tx.transaction_hash = calculate_tx_hash(tx)
    return tx


def run_multiblock_test():
    print("--- Starting Mutli-Block Simulation ---\n")
    blockchain = Blockchain()

    # using an easy difficulty
    difficulty_bits = 0x207FFFFF

    priv, pub = generate_key()

    print("\n--- Mining Block 1 ---")
    tx1 = generate_mock_tx(priv, pub, 5, 12)
    tx2 = generate_mock_tx(priv, pub, 6, 11)

    tip = blockchain.get_tip()
    block1 = construct_and_mine_block(tip, [tx1, tx2], difficulty_bits)

    if block1:
        success = blockchain.add_block(block1)
        print(f"Block 1 Appended: {success}")
        print(
            f"Block 1 Hash: {block1.header.hash_prev_block} (prev) -> Merkle: {block1.header.hash_merkle_root}"
        )
    else:
        print("Failed to mine Block 1")
        return

    print("\n--- Mining Block 2 ---")
    tx3 = generate_mock_tx(priv, pub, 4, 13)

    tip = blockchain.get_tip()
    block2 = construct_and_mine_block(tip, [tx3], difficulty_bits)

    if block2:
        success = blockchain.add_block(block2)
        print(f"Block 2 Appended: {success}")
        print(
            f"Block 2 Hash: {block2.header.hash_prev_block} (prev) -> Merkle: {block2.header.hash_merkle_root}"
        )
    else:
        print("Failed to mine Block 2")
        return

    print("\n--- Analyzing Blockchain ---")
    print(f"Total Blocks: {len(blockchain.blocks)}")
    for i, b in enumerate(blockchain.blocks):
        print(
            f"Height: {b.header.height}, PrevHash: {b.header.hash_prev_block[:16]}..., Tx Count: {len(b.transactions)}"
        )


if __name__ == "__main__":
    run_multiblock_test()
