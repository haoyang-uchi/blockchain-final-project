# test_basic.py

from core.cryptography import sign_tx, verify_tx_signature
from core.wallet import Wallet
from core.state import State
from state.validation import validate_order_tx, ValidationContext
from core.trade import create_trade_tx
import proto.energy_chain_pb2 as pb2


def test_basic():
    # setting up keypairs
    print("--- Setting Up Keypairs ---\n")
    grid_wallet = Wallet.generate()
    user_wallet = Wallet.generate()
    miner_wallet = Wallet.generate()

    grid_priv, grid_pub = grid_wallet.private_key_hex, grid_wallet.public_key_hex
    user_priv, user_pub = user_wallet.private_key_hex, user_wallet.public_key_hex
    miner_priv, miner_pub = miner_wallet.private_key_hex, miner_wallet.public_key_hex

    print(f"Grid PubKey: {grid_pub[:16]}...")
    print(f"User PubKey: {user_pub[:16]}...")
    print(f"Miner PubKey: {miner_pub[:16]}...")

    # grid broadcasts rates
    print("\n--- Grid Broadcasting Rates ---")
    grid_rate = pb2.GridRateTx()
    grid_rate.push_rate = 4  # pays 5 microcoins per Wh
    print(f"Grid TX: Rates -> PUSH: {grid_rate.push_rate}, PULL: {grid_rate.pull_rate}")
    grid_rate.pull_rate = 12  # charges 12 microcoins per Wh
    print(f"Grid TX: Rates -> PUSH: {grid_rate.push_rate}, PULL: {grid_rate.pull_rate}")
    grid_rate.expiry_height = 100
    grid_rate.grid_address = grid_pub

    # wrap in transaction and sign
    grid_tx = pb2.Transaction()
    grid_tx.grid_rate_tx.CopyFrom(grid_rate)
    sign_tx(grid_tx, grid_priv)

    is_valid = verify_tx_signature(grid_tx)
    print(f"Grid TX: Signature Valid: {is_valid}")
    print(f"Grid TX: Rates -> PUSH: {grid_rate.push_rate}, PULL: {grid_rate.pull_rate}")

    # creating a test order
    print("\n--- Creating an Order ---")
    order = pb2.OrderTx()
    order.sender_address = user_pub
    order.type = pb2.PUSH  # selling
    order.energy_wh = 500
    order.limit_price = 4  # will only sell if Grid pays at least 4
    order.nonce = 1

    # add the script: only execute if the pull rate is less than 15
    order.script = "GET_PULL_RATE 15 LT VERIFY 1"

    # wrap in a transacton and sign it
    order_tx = pb2.Transaction()
    order_tx.order_tx.CopyFrom(order)
    sign_tx(order_tx, user_priv)

    is_valid = verify_tx_signature(order_tx)
    print(f"Order tx: Signature Valid: {is_valid}")
    print(f"Order tx: Selling {order.energy_wh} Wh. Limit: {order.limit_price}.")
    print(f"Order tx: Script: '{order.script}'")

    # mock state to fulfill balance requirements
    state = State()
    state.get_account(user_pub).energy_wh = 1000

    ctx = ValidationContext(height=50, grid_rate=grid_rate)
    
    can_execute, reason = validate_order_tx(order_tx, ctx, state)

    print(f"Miner: evaluate_order() result: {can_execute} {reason}")

    if can_execute:
        # miner is settling the trade
        miner_fee = 50  # miner is taking 50 microcoins
        trade_tx = create_trade_tx(order, grid_rate, miner_pub, miner_fee)

        trade = trade_tx.trade_tx
        print("\n--- Settling the Trade ---")
        print(f"Trade tx: Successfully created settlement!")
        print(f"Trade tx: Settled Amount: {trade.settlement_amount} microcoins")
        print(f"Trade tx: Miner Fee Collected: {trade.miner_fee}")
    else:
        print("\nTrade tx: Execution failed!")


if __name__ == "__main__":
    test_basic()
