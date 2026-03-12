## MPCS 56600: Final Project

## Group Members

| Name | CNET | GitHub |
| :--- | :--- | :--- |
| Clarice Kim | claricek | cnk2-rgb |
| Spencer Dearman | dearmanspencer | spencerdearman |
| Haoyang Li | haoyangl | haoyang-uchi |
| Kevin Dougherty | kdough01 | kdough01 |


## Running Tests
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
python3 scripts/advanced_script_test.py
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
