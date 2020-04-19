#!/bin/bash

if [ "$EUID" -ne 0 ]; then
        echo "Please run as root/superuser...!!!"
        exit
fi

printf "\n# Forcefully removing containers created with network bridge-nw...\n"
docker rm -f $(docker ps -aq -f network=bridge-nw)

printf "\n\n# Removing images for sender, receiver and rabbitmq:management...\n"
docker rmi sender:latest
docker rmi receiver:latest
docker rmi rabbitmq:management

printf "\n\n# Removing docker name bridge-nw...\n"
docker network rm bridge-nw
