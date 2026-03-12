## MPCS 56600: Final Project

## Group Members

| Name | CNET | GitHub |
| :--- | :--- | :--- |
| Clarice Kim | claricek | cnk2-rgb |
| Spencer Dearman | dearmanspencer | spencerdearman |
| Haoyang Li | haoyangl | haoyang-uchi |
| Kevin Dougherty | kdough01 | kdough01 |

## CLI

`cli/cli.py` is the command-line interface for the project. It creates or loads wallets, builds and signs transactions locally, and sends them to a blockchain node over gRPC.

#### Basic Command

##### Initialize Wallet
```bash
python -m cli.cli init-wallet --wallet testing_ground/user_a.json
```

###### Post Quote
```bash
python -m cli.cli post-quote --bid 5 --ask 12 --expiry 1000000 --wallet grid_wallet.json --node 127.0.0.1:58334
```

###### Buy Energy
```bash
python -m cli.cli buy --energy-wh 100 --limit-price 12 --expiry 1000000 --nonce 1 --script "1" --wallet testing_ground/user_a.json --node 127.0.0.1:58334
```

###### Sell Energy
```bash
python -m cli.cli sell --energy-wh 80 --limit-price 5 --expiry 1000000 --nonce 2 --script "1" --wallet testing_ground/user_a.json --node 127.0.0.1:58334
```

###### Request Faucet Funds
```bash
python -m cli.cli faucet --wallet testing_ground/user_a.json --node 127.0.0.1:58334
```

###### Check Balance
```bash
python -m cli.cli balance --wallet testing_ground/user_a.json --node 127.0.0.1:58334
```

###### Check Node Status
```bash
python -m cli.cli status --node 127.0.0.1:58334
```

#### Advance Command

###### Buy only if the current pull rate is below 20
```bash
python -m cli.cli buy --energy-wh 10 --limit-price 12 --expiry 1000000 --nonce 1 --script "GET_PULL_RATE 20 LT VERIFY 1" --wallet testing_ground/user_a.json --node 127.0.0.1:58334
```

###### Sell only if the current push rate equals 5
```bash
python -m cli.cli sell --energy-wh 10 --limit-price 5 --expiry 1000000 --nonce 2 --script "GET_PUSH_RATE 5 EQ" --wallet testing_ground/user_a.json --node 127.0.0.1:58334
```

###### Buy only if the current block height is greater than 100
```bash
python -m cli.cli buy --energy-wh 10 --limit-price 12 --expiry 1000000 --nonce 3 --script "GETHEIGHT 100 GT" --wallet testing_ground/user_a.json --node 127.0.0.1:58334
```


## Running Automatic Tests
1. In terminal 1 start the docker container
```bash
docker compose up --build
```
2. In terminal 2, run the test script:
- **Basic Test**
```bash
python3 scripts/basic_test.py
```
- **Advanced Test**
```bash
python3 scripts/advanced_test.py
```
3. Once it completes, then in terminal 1 shutdown docker
```bash
docker compose down
```


## Sources
- Proto syntax: https://protobuf.dev/programming-guides/proto3/
- Proto formatter: https://formatter.org/protobuf-formatter
- gRPC syntax + Python code generation: https://grpc.io/docs/languages/python/quickstart/
- Hash functions: https://docs.python.org/3/library/hashlib.html
- Python formatter: https://codebeautify.org/python-formatter-beautifier
- ECDSA: https://pypi.org/project/ecdsa/
- Black Python formatter: https://pypi.org/project/black/
- Config parser: https://medium.com/the-pythonworld/how-to-write-and-use-configuration-files-in-python-like-a-pro-8465126ca055 
- Threadsafe queue implementation: https://docs.python.org/3/library/queue.html
- Creating the gRPC server: https://grpc.io/docs/languages/python/basics/
- Adding sys path to fix the module issues: https://www.geeksforgeeks.org/python/sys-path-in-python/
- Dockerfile setup: https://www.geeksforgeeks.org/cloud-computing/what-is-dockerfile/
