# assumes build run first
# make sure to also pass it a container name
docker run -it --rm --name $1 --link DNS_SEED:grpc_server network /bin/bash 