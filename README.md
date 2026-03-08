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
This section will be cleaned up

Building the docker image for all nodes:
```bash
cd ./net
docker build -t node-image .
```

Helpful tips:
- Remember to restart the docker server to reset the cache of known nodes. 

## Sources
- Proto syntax: https://protobuf.dev/programming-guides/proto3/
- Proto formatter: https://formatter.org/protobuf-formatter
- gRPC syntax + Python code generation: https://grpc.io/docs/languages/python/quickstart/
- Hash functions: https://docs.python.org/3/library/hashlib.html
- Python formatter: https://codebeautify.org/python-formatter-beautifier
- ECDSA: https://pypi.org/project/ecdsa/
- Black Python formatter: https://pypi.org/project/black/
