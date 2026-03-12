# scripts/automate_test.py

import os
import sys

root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root)

import subprocess
import time

NODE = "localhost:58334"
WALLET = "test_user.json"


def run_cli(args):
    cmd = [sys.executable, os.path.join(root, "cli", "cli.py")] + args
    if "--node" not in args and "init-wallet" not in args:
        cmd += ["--node", NODE]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return f"ERROR: {result.stderr}"
    return result.stdout.strip()


def main():
    print("Basic Test")

    # check connection
    print(f"Connecting to node {NODE}...")
    time.sleep(2)
    status = run_cli(["status"])
    if "ERROR" in status:
        print(f"Could not connect.")
        return
    print(f"Connected. Chain Height: {status}")

    # create a wallet
    print("\n--- Initializing New Wallet ---")
    out = run_cli(["init-wallet", "--wallet", WALLET])
    print(out)
    pub_key = (
        out.split("Public key: ")[1].strip() if "Public key: " in out else "Unknown"
    )
    print(f"Target Address: {pub_key[:16]}...")

    # wait for the faucet to allocate funds
    print("\n--- Waiting for Faucet Funding ---")
    print("Polling node for balance update...")

    retries = 25
    funded = False
    while retries > 0:
        balance_out = run_cli(["balance", "--wallet", WALLET])
        if "Coins:  5000000" in balance_out:
            print("\n[SUCCESS] Wallet funded!")
            print(balance_out)
            funded = True
            break

        summary = balance_out.replace("\n", " | ")
        print(f"Still waiting... (Retries: {retries}) Current: {summary}")
        time.sleep(5)
        retries -= 1

    if not funded:
        print("\n[TIMEOUT] Faucet grant not seen in time.")
        print("Nodes might still be mining. Check: docker compose logs -f node_a")
        return

    # buy energy test
    print("\n--- Buy Order Test ---")
    buy_res = run_cli(
        [
            "buy",
            "--energy-wh",
            "250",
            "--limit-price",
            "600",
            "--expiry",
            "50",
            "--nonce",
            "1",
            "--script",
            "1 1 EQ",
            "--wallet",
            WALLET,
        ]
    )
    print(buy_res)

    # verify
    print("\n--- Verify ---")
    for i in range(3):
        print(f"Mining... {15 - i*5}s left")
        time.sleep(5)

    print("\n--- Final Status ---")
    print(run_cli(["balance", "--wallet", WALLET]))
    print("\nTest Complete!")


if __name__ == "__main__":
    main()
