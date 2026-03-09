# tests/test_consensus.py

from core.blockchain import Blockchain
from core.wallet import Wallet
from core.miner import construct_and_mine_block
from core.block import create_new_block, calculate_header_hash
import proto.energy_chain_pb2 as pb2

def test_add_block_success():
    bc = Blockchain()
    tip = bc.get_tip()

    # create a mock order and trade transaction
    # (Leaving transactions empty for a simple valid mined block)
    mined_block = construct_and_mine_block(tip, [], difficulty_bits=0x207FFFFF)
    
    success = bc.add_block(mined_block)
    assert success is True
    assert len(bc.blocks) == 2

def test_add_block_invalid_pow():
    bc = Blockchain()
    tip = bc.get_tip()

    # create a block without mining (using a hard difficulty so nonce=0 fails)
    bad_block = create_new_block(calculate_header_hash(tip.header), height=tip.header.height + 1, bits=0x1D00FFFF)
    bad_block.header.nonce = 0 # likely invalid
    
    success = bc.add_block(bad_block)
    # The block should be rejected because PoW is invalid
    assert success is False
    assert len(bc.blocks) == 1

if __name__ == "__main__":
    test_add_block_success()
    test_add_block_invalid_pow()
    print("Consensus tests passed!")
