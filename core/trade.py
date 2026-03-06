# core/trade.py

import proto.energy_chain_pb2 as pb2
from scripting.script_engine import ScriptEngine
from core.block import calculate_tx_hash


def evaluate_order(order_tx: pb2.OrderTx, grid_rate: pb2.GridRateTx, height: int):
    # producer will sell if the push rate >= limit price
    if order_tx.type == pb2.PUSH:
        if grid_rate.push_rate < order_tx.limit_price:
            print(
                f"Order PUSH limit failed: {grid_rate.push_rate} < {order_tx.limit_price}"
            )
            return False
    else:
        # consumer will buy if the grid pull rate <= limit price
        if grid_rate.pull_rate > order_tx.limit_price:
            print(
                f"Order PULL limit failed: {grid_rate.pull_rate} > {order_tx.limit_price}"
            )
            return False

    # otherwise run the script with context
    context = {
        "height": height,
        "push_rate": grid_rate.push_rate,
        "pull_rate": grid_rate.pull_rate,
    }
    engine = ScriptEngine(order_tx.script, context)
    if not engine.execute():
        print("Script execution failed.")
        return False
    return True


# creates a TradeTx based on the Order on the grid.
def create_trade_tx(
    order_tx: pb2.OrderTx, grid_rate: pb2.GridRateTx, miner_address: str, fee: int
) -> pb2.Transaction:
    trade = pb2.TradeTx()
    trade.miner_address = miner_address
    trade.order.CopyFrom(order_tx)
    trade.grid_rate.CopyFrom(grid_rate)
    trade.miner_fee = fee

    # calculating the settlement
    if order_tx.type == pb2.PUSH:
        # user sells energy means settlement = energy_wh * push_rate
        trade.settlement_amount = order_tx.energy_wh * grid_rate.push_rate
    else:
        # user buys energy means settlement = energy_wh * pull_rate
        trade.settlement_amount = order_tx.energy_wh * grid_rate.pull_rate

    tx = pb2.Transaction()
    tx.trade_tx.CopyFrom(trade)
    tx.transaction_hash = calculate_tx_hash(tx)
    return tx
