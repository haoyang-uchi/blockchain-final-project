# state/validation.py

from core.state import State, GRID_ADDRESS
from core.cryptography import verify_tx_signature
from scripting.script_engine import ScriptEngine
import proto.energy_chain_pb2 as pb2

"""
These are just basically whatever tests I could think of to validate
the orders, quotes, trades, and grid rates.
"""


class ValidationContext:
    def __init__(self, height, grid_rate):
        self.height = height
        self.grid_rate = grid_rate


def validate_order_tx(tx, ctx, state):
    if not tx.HasField("order_tx"):
        return False, "Transaction does not contain an OrderTx"

    order = tx.order_tx

    if not verify_tx_signature(tx):
        return False, "OrderTx invalid signature"

    account = state.get_account(order.sender_address)

    # bypass checks for new wallets
    if order.script == "FAUCET":
        if order.nonce != 0:
            return False, "FAUCET request only allowed with nonce 0"
        if account.micro_coins > 0 or account.energy_wh > 0 or account.nonce > 0:
            return False, "FAUCET only allowed for new, empty accounts"
        return True, ""

    if ctx.grid_rate is None:
        return False, "OrderTx no active GridRateTx, cannot evaluate order"

    gr = ctx.grid_rate

    if gr.expiry_height <= ctx.height:
        return False, f"OrderTx: active grid rate expired at height {gr.expiry_height}"

    if order.energy_wh <= 0:
        return False, f"OrderTx energy_wh must be positive, got {order.energy_wh}"

    if order.limit_price <= 0:
        return False, f"OrderTx limit_price must be positive, got {order.limit_price}"

    expected_nonce = account.nonce + 1
    if order.nonce != expected_nonce:
        return (
            False,
            f"OrderTx bad nonce for {order.sender_address[:16]}, expected {expected_nonce}, got {order.nonce}",
        )

    if order.type == pb2.PUSH:
        if gr.push_rate < order.limit_price:
            return (
                False,
                f"OrderTx PUSH limit {order.limit_price} not met by grid push_rate {gr.push_rate}",
            )

    elif order.type == pb2.PULL:
        if gr.pull_rate > order.limit_price:
            return (
                False,
                f"OrderTx: PULL limit {order.limit_price} not met by grid pull_rate {gr.pull_rate}",
            )

    else:
        return False, f"OrderTx unknown order type {order.type}"

    context = {
        "height": ctx.height,
        "push_rate": gr.push_rate,
        "pull_rate": gr.pull_rate,
    }
    engine = ScriptEngine(order.script, context)
    if not engine.execute():
        return False, "OrderTx script execution failed"

    if order.type == pb2.PUSH:
        if account.energy_wh < order.energy_wh:
            return (
                False,
                f"OrderTx: insufficient energy for {order.sender_address[:16]}, has {account.energy_wh} wh, needs {order.energy_wh} wh",
            )

    else:
        settlement = order.energy_wh * gr.pull_rate
        if account.micro_coins < settlement:
            return (
                False,
                f"OrderTx: insufficient coins for {order.sender_address[:16]}, has {account.micro_coins}, needs at least {settlement}",
            )

    return True, ""


def validate_trade_tx(tx, ctx, state):
    if not tx.HasField("trade_tx"):
        return False, "Transaction does not contain a TradeTx"

    trade = tx.trade_tx

    order_wrapper = pb2.Transaction()
    order_wrapper.order_tx.CopyFrom(trade.order)
    ok, reason = validate_order_tx(order_wrapper, ctx, state)
    if not ok:
        return False, f"TradeTx: embedded order invalid — {reason}"

    if ctx.grid_rate is None:
        return False, "TradeTx: no active GridRateTx in context"
    if (
        trade.grid_rate.push_rate != ctx.grid_rate.push_rate
        or trade.grid_rate.pull_rate != ctx.grid_rate.pull_rate
    ):
        return (
            False,
            f"TradeTx: embedded grid_rate (push={trade.grid_rate.push_rate}, pull={trade.grid_rate.pull_rate}) does not match active rate (push={ctx.grid_rate.push_rate}, pull={ctx.grid_rate.pull_rate})",
        )

    order = trade.order
    if order.type == pb2.PUSH:
        expected_settlement = order.energy_wh * ctx.grid_rate.push_rate
    else:
        expected_settlement = order.energy_wh * ctx.grid_rate.pull_rate

    if trade.settlement_amount != expected_settlement:
        return (
            False,
            f"TradeTx settlement_amount {trade.settlement_amount} not the expected {expected_settlement}",
        )

    if trade.miner_fee < 0:
        return False, f"TradeTx miner_fee cannot be negative, got {trade.miner_fee}"

    user = state.get_account(order.sender_address)
    grid = state.get_account(GRID_ADDRESS)

    if order.type == pb2.PUSH:
        if user.energy_wh < order.energy_wh:
            return (
                False,
                f"TradeTx: user {order.sender_address[:16]}… has {user.energy_wh} wh, needs {order.energy_wh} wh",
            )

        if grid.micro_coins < trade.settlement_amount + trade.miner_fee:
            return (
                False,
                f"TradeTx: grid has {grid.micro_coins} coins, needs {trade.settlement_amount + trade.miner_fee}",
            )

    else:
        total_cost = trade.settlement_amount + trade.miner_fee
        if user.micro_coins < total_cost:
            return (
                False,
                f"TradeTx: user {order.sender_address[:16]}… has {user.micro_coins} coins, needs {total_cost}",
            )

        if grid.energy_wh < order.energy_wh:
            return (
                False,
                f"TradeTx grid has {grid.energy_wh} wh, needs {order.energy_wh} wh",
            )

    return True, ""


def validate_grid_rate_tx(tx, ctx, state):
    if not tx.HasField("grid_rate_tx"):
        return False, "Transaction does not contain a GridRateTx"

    gx = tx.grid_rate_tx

    if not verify_tx_signature(tx):
        return False, "GridRateTx: invalid signature"

    if gx.push_rate <= 0:
        return (
            False,
            f"GridRateTx must have a positive push_rate, but got {gx.push_rate}",
        )

    if gx.pull_rate <= 0:
        return (
            False,
            f"GridRateTx must have a positive pull_rate, but got {gx.pull_rate}",
        )

    if gx.push_rate > gx.pull_rate:
        return (
            False,
            f"GridRateTx push_rate ({gx.push_rate}) must be less than or equal to the pull_rate ({gx.pull_rate})",
        )

    if gx.expiry_height <= ctx.height:
        return (
            False,
            f"GridRateTx rate expired at height {gx.expiry_height}, current height {ctx.height}",
        )

    if gx.grid_address != GRID_ADDRESS:
        return (
            False,
            f"GridRateTx: grid_address mismatch, expected {GRID_ADDRESS}, got {gx.grid_address}",
        )

    return True, ""
