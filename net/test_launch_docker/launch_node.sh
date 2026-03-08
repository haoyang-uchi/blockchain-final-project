# assumes build run first
# make sure to also pass it a container name
# --rm Automatically removes container after exiting interactive mode (for debugging)
docker run -it --rm --name $1 --link DNS_SEED:grpc_server network /bin/bash 