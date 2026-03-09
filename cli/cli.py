import argparse
import grpc

import network.config as net_config
import proto.energy_chain_pb2 as pb2
import proto.energy_chain_pb2_grpc as pb2_grpc
from core.wallet import Wallet
from core.block import calculate_tx_hash
from core.cryptography import sign_tx


DEFAULT_WALLET_PATH = "wallet.json"


def _normalize_node_target(node: str) -> str:
    if ":" in node:
        return node
    return f"{node}:{net_config.PORT}"


def _submit_tx(node: str, tx: pb2.Transaction):
    target = _normalize_node_target(node)
    channel = grpc.insecure_channel(target)
    stub = pb2_grpc.NodeServiceStub(channel)
    return stub.SubmitTx(tx)


def _get_tip(node: str):
    target = _normalize_node_target(node)
    channel = grpc.insecure_channel(target)
    stub = pb2_grpc.NodeServiceStub(channel)
    return stub.GetTip(pb2.GetTipRequest())


def _load_wallet(wallet_path: str) -> Wallet:
    return Wallet.load(wallet_path)


def cmd_init_wallet(args):
    wallet = Wallet.generate()
    wallet.save(args.wallet)
    print(f"Wallet saved to {args.wallet}")
    print(f"Public key: {wallet.public_key_hex}")


def cmd_post_quote(args):
    wallet = _load_wallet(args.wallet)

    quote = pb2.GridRateTx()
    quote.push_rate = args.bid
    quote.pull_rate = args.ask
    quote.expiry_height = args.expiry
    quote.grid_address = wallet.public_key_hex

    tx = pb2.Transaction()
    tx.grid_rate_tx.CopyFrom(quote)
    sign_tx(tx, wallet.private_key_hex)
    tx.transaction_hash = calculate_tx_hash(tx)

    try:
        response = _submit_tx(args.node, tx)
        print(f"SubmitTx success={response.success} message='{response.message}'")
        print(f"tx_hash={tx.transaction_hash}")
    except grpc.RpcError as e:
        print(f"SubmitTx RPC failed: {e.code().name} {e.details()}")


def _build_order_tx(wallet: Wallet, side: str, args):
    order = pb2.OrderTx()
    order.sender_address = wallet.public_key_hex
    order.type = pb2.PULL if side == "buy" else pb2.PUSH
    order.energy_wh = args.energy_wh
    order.limit_price = args.limit_price
    order.nonce = args.nonce
    order.script = args.script

    tx = pb2.Transaction()
    tx.order_tx.CopyFrom(order)
    sign_tx(tx, wallet.private_key_hex)
    tx.transaction_hash = calculate_tx_hash(tx)
    return tx


def cmd_buy(args):
    wallet = _load_wallet(args.wallet)
    tx = _build_order_tx(wallet, "buy", args)
    try:
        response = _submit_tx(args.node, tx)
        print(f"SubmitTx success={response.success} message='{response.message}'")
        print(f"tx_hash={tx.transaction_hash}")
    except grpc.RpcError as e:
        print(f"SubmitTx RPC failed: {e.code().name} {e.details()}")


def cmd_sell(args):
    wallet = _load_wallet(args.wallet)
    tx = _build_order_tx(wallet, "sell", args)
    try:
        response = _submit_tx(args.node, tx)
        print(f"SubmitTx success={response.success} message='{response.message}'")
        print(f"tx_hash={tx.transaction_hash}")
    except grpc.RpcError as e:
        print(f"SubmitTx RPC failed: {e.code().name} {e.details()}")


def cmd_status(args):
    try:
        tip = _get_tip(args.node)
        tx_count = len(tip.transactions)
        print(
            f"tip_height={tip.header.height} prev_hash={tip.header.hash_prev_block} tx_count={tx_count}"
        )
    except grpc.RpcError as e:
        print(f"GetTip RPC failed: {e.code().name} {e.details()}")


def build_parser():
    parser = argparse.ArgumentParser(description="Energy Trading Chain CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_init = subparsers.add_parser("init-wallet")
    p_init.add_argument("--wallet", default=DEFAULT_WALLET_PATH)
    p_init.set_defaults(func=cmd_init_wallet)

    p_quote = subparsers.add_parser("post-quote")
    p_quote.add_argument("--bid", type=int, required=True)
    p_quote.add_argument("--ask", type=int, required=True)
    p_quote.add_argument("--expiry", type=int, required=True)
    p_quote.add_argument("--node", required=True)
    p_quote.add_argument("--wallet", default=DEFAULT_WALLET_PATH)
    p_quote.set_defaults(func=cmd_post_quote)

    p_buy = subparsers.add_parser("buy")
    p_buy.add_argument("--energy-wh", type=int, required=True, dest="energy_wh")
    p_buy.add_argument("--limit-price", type=int, required=True, dest="limit_price")
    p_buy.add_argument("--expiry", type=int, required=True)
    p_buy.add_argument("--nonce", type=int, default=1)
    p_buy.add_argument("--script", default="1")
    p_buy.add_argument("--node", required=True)
    p_buy.add_argument("--wallet", default=DEFAULT_WALLET_PATH)
    p_buy.set_defaults(func=cmd_buy)

    p_sell = subparsers.add_parser("sell")
    p_sell.add_argument("--energy-wh", type=int, required=True, dest="energy_wh")
    p_sell.add_argument("--limit-price", type=int, required=True, dest="limit_price")
    p_sell.add_argument("--expiry", type=int, required=True)
    p_sell.add_argument("--nonce", type=int, default=1)
    p_sell.add_argument("--script", default="1")
    p_sell.add_argument("--node", required=True)
    p_sell.add_argument("--wallet", default=DEFAULT_WALLET_PATH)
    p_sell.set_defaults(func=cmd_sell)

    p_status = subparsers.add_parser("status")
    p_status.add_argument("--node", required=True)
    p_status.set_defaults(func=cmd_status)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
