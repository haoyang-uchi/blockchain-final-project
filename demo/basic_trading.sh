#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"


python -m cli.cli faucet --wallet testing_ground/demo_user_a.json --node 127.0.0.1:58334
python -m cli.cli faucet --wallet testing_ground/demo_user_b.json --node 127.0.0.1:58334

sleep 4

python -m cli.cli balance --wallet testing_ground/demo_user_a.json --node 127.0.0.1:58334
python -m cli.cli balance --wallet testing_ground/demo_user_b.json --node 127.0.0.1:58334


python -m cli.cli buy --energy-wh 120 --limit-price 12 --expiry 1000000 --nonce 1 --script "1" --wallet testing_ground/demo_user_a.json --node 127.0.0.1:58334
python -m cli.cli sell --energy-wh 70 --limit-price 5 --expiry 1000000 --nonce 1 --script "1" --wallet testing_ground/demo_user_b.json --node 127.0.0.1:58334

sleep 4

python -m cli.cli balance --wallet testing_ground/demo_user_a.json --node 127.0.0.1:58334
python -m cli.cli balance --wallet testing_ground/demo_user_b.json --node 127.0.0.1:58334
python -m cli.cli status --node 127.0.0.1:58334
