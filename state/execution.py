import proto.energy_chain_pb2 as pb2
from core.state import State, GRID_ADDRESS
from state.validation import ValidationContext, validate_grid_rate_tx, validate_order_tx, validate_trade_tx
from core.block import calculate_header_hash

def apply_block(block, state):
    """
    This applied all transactions in a block to a copy of the state
    """
    working = state.copy()
    height = block.header.height

    ctx = ValidationContext(height=height, grid_rate=working.active_grid_rate)

    grid_rate_txs = []
    order_txs = []
    trade_txs = []

    for tx in block.transactions:
        payload = tx.WhichOneof("payload")
        if payload == "grid_rate_tx":
            grid_rate_txs.append(tx)
        elif payload == "order_tx":
            order_txs.append(tx)
        elif payload == "trade_tx":
            trade_txs.append(tx)
        else:
            return state, False, f"Unknown transaction payload type in block at height {height}"

    for tx in grid_rate_txs:
        ok, reason = validate_grid_rate_tx(tx, ctx, working)
        if not ok:
            return state, False, f"GridRateTx invalid: {reason}"
        ctx = ValidationContext(height=height, grid_rate=tx.grid_rate_tx)
        working.active_grid_rate = tx.grid_rate_tx

    for tx in order_txs:
        ok, reason = validate_order_tx(tx, ctx, working)
        if not ok:
            return state, False, f"OrderTx invalid: {reason}"
        
        ord = tx.order_tx
        account = working.get_account(ord.sender_address)
        
        # incremenet for a real trade but not for faucet
        if ord.script != "FAUCET":
            account.nonce = ord.nonce

        # faucet: give funds from the grid to a new user
        if ord.script == "FAUCET":
            grid = working.get_account(GRID_ADDRESS)
            grant_coins = 5_000_000
            grant_energy = 5_000
            
            # transfer
            grid.micro_coins -= grant_coins
            grid.energy_wh -= grant_energy
            account.micro_coins += grant_coins
            account.energy_wh += grant_energy
            
            print(f"Faucet: granted {grant_coins} coins and {grant_energy} Wh to {ord.sender_address[:16]}...")

    for tx in trade_txs:
        ok, reason = validate_trade_tx(tx, ctx, working)
        if not ok:
            return state, False, f"TradeTx invalid: {reason}"

        trade = tx.trade_tx
        order = trade.order
        is_push = (order.type == pb2.PUSH)

        working.apply_trade(
            user_address=order.sender_address,
            energy_amount=order.energy_wh,
            settlement_amount=trade.settlement_amount,
            push=is_push,
            fee=trade.miner_fee,
            miner_address=trade.miner_address,
            nonce=order.nonce,
        )

    return working, True, ""