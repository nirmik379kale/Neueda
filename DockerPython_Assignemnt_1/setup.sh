#!/bin/bash

if [ "$EUID" -ne 0 ]; then 
	echo "Please run as root/superuser...!!!"
  	exit
fi

printf "\n# Creating a Docker Network (type bridge)...\n"
docker network create -d bridge bridge-nw

printf "\n\n# Building docker image for sender container...\n"
docker build -t sender sender/

printf "\n\n# Building docker image for receiver container...\n"
docker build -t receiver receiver/

printf "\n\n# Creating a directory called output to store the generated xml files in receiver container\n"
mkdir output

printf "\n\n# Run RabbitMQ Container in network created above\n"
docker run -d --restart always --hostname rabbitqueue --name rabbitqueue --network bridge-nw rabbitmq:management
