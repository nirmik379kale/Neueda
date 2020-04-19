#!/bin/bash

if [ "$EUID" -ne 0 ]; then
        echo "Please run as root/superuser...!!!"
        exit
fi

printf "\n# Executing sender container which will send the encrypted data over rabbitmq.\n" 
# I have kept sample jsons in /jsons/ directory inside container. If you want to test with your jsons you can mount a volume by adding parameter `-v /path/to/your/jsons:/jsons so container can read .json files from.

docker run --network bridge-nw sender

# you can also run this command with --rm arg as this is executable container and will exit as soon as its task is completed.

printf "\n\n# Lets receive this file from another container\n"

docker run --network bridge-nw -v `pwd`/output:/xmls receiver

printf "# Here we are mounting output directory which we created in setup file. It will store the received xmls.\n"
