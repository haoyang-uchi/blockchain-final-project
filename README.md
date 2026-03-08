## MPCS 56600: Final Project

## Group Members

| Name | CNET | GitHub |
| :--- | :--- | :--- |
| Clarice Kim | claricek | cnk2-rgb |
| Spencer Dearman | dearmanspencer | spencerdearman |
| Haoyang Li | haoyangl | haoyang-uchi |
| Kevin Dougherty | kdough01 | kdough01 |

## Tests
```bash
python3 -m tests.test_basic
python3 -m tests.test_multiblock
```

## Networking
Downloading GRPC packages: 
pip3 install -r requirements.txt

Building the docker image for all nodes:
```bash
cd ./net
docker build -t node-image .
```

Helpful development tips:
- Use config parser for the network port
- Remember to restart the docker server to reset the cache of known nodes. 
- If GRPC gives you any difficulties, sometimes you need to run the following: 
```bash
pip3 install --upgrade google-api-python-client
```
- To regenerate the python files after editing anything in the proto directory, run the following:
```bash
cd ./proto
bash proto_2_py.sh
```

Clarice's Notes for her PR (will delete later):
- Decided to create separate proto services for registrar nodes and regular nodes due to the fact I need to store different logic for registrar and regular node classes. 

## Sources
- Proto syntax: https://protobuf.dev/programming-guides/proto3/
- Proto formatter: https://formatter.org/protobuf-formatter
- gRPC syntax + Python code generation: https://grpc.io/docs/languages/python/quickstart/
- Hash functions: https://docs.python.org/3/library/hashlib.html
- Python formatter: https://codebeautify.org/python-formatter-beautifier
- ECDSA: https://pypi.org/project/ecdsa/
- Black Python formatter: https://pypi.org/project/black/
- Config parser: https://medium.com/the-pythonworld/how-to-write-and-use-configuration-files-in-python-like-a-pro-8465126ca055 
