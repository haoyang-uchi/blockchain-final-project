#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python -m cli.cli init-wallet --wallet testing_ground/demo_user_a.json
python -m cli.cli faucet --wallet testing_ground/demo_user_a.json --node 127.0.0.1:58334

sleep 6

echo "CASE 1: pass with GET_PULL_RATE LT VERIFY"
python -m cli.cli buy --energy-wh 10 --limit-price 12 --expiry 1000000 --nonce 1 --script "GET_PULL_RATE 20 LT VERIFY 1" --wallet testing_ground/demo_user_a.json --node 127.0.0.1:58334

echo "CASE 2: fail with GET_PULL_RATE LT VERIFY"
python -m cli.cli buy --energy-wh 10 --limit-price 12 --expiry 1000000 --nonce 2 --script "GET_PULL_RATE 5 LT VERIFY 1" --wallet testing_ground/demo_user_a.json --node 127.0.0.1:58334

echo "CASE 3: pass with GET_PUSH_RATE EQ"
python -m cli.cli sell --energy-wh 10 --limit-price 5 --expiry 1000000 --nonce 2 --script "GET_PUSH_RATE 5 EQ" --wallet testing_ground/demo_user_a.json --node 127.0.0.1:58334

echo "CASE 4: fail with GETHEIGHT GT"
python -m cli.cli buy --energy-wh 10 --limit-price 12 --expiry 1000000 --nonce 3 --script "GETHEIGHT 999999 GT" --wallet testing_ground/demo_user_a.json --node 127.0.0.1:58334

echo "CASE 5: pass with DUP AND"
python -m cli.cli buy --energy-wh 10 --limit-price 12 --expiry 1000000 --nonce 3 --script "1 DUP AND" --wallet testing_ground/demo_user_a.json --node 127.0.0.1:58334

echo "CASE 6: fail with DROP leaving empty stack"
python -m cli.cli buy --energy-wh 10 --limit-price 12 --expiry 1000000 --nonce 4 --script "1 DROP" --wallet testing_ground/demo_user_a.json --node 127.0.0.1:58334

sleep 8

python -m cli.cli balance --wallet testing_ground/demo_user_a.json --node 127.0.0.1:58334
python -m cli.cli status --node 127.0.0.1:58334
