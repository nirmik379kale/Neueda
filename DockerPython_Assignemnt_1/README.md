#Container Based XML File Transfer

- This project converts json to xml and transfers an encrypted version of this xml from one docker container to another.
- The order of operations in this project are as follows :
    Json -> XML -> encryption -> transfer -> decryption -> XML 
    
    which is divided as :
	- Json -> XML -> encryption -> push : Task of sender.py (sender container) 
 	- transfer : Task for rabbitmq container
	- receive -> decryption -> XML : Tasks for receiver.py (receiver container)

---

## How to execute?

Once your moved to this project subdirectory, you will see bunch of files.

- `setup.sh`
: This script will setup the system which includes :
    - build container images
    - create bridge network 
    - run the rabbitmq container.

- `execute.sh`
: This will execute the containers that we just built images of which are 
    1. sender
    2. receiver 
  
  - There are sample json files located under `sender/jsons/` subdirectory inside the container.
  - This script will first execute the sender container and then will execute the receiver container but if you want you can execute the commands given for running sender and receiver container in two different terminals. The received files are stored in output directory which setup.sh script created while setting up your environment. Please check this script for mount args.

- `cleanup.sh`
: This script will cleanup : 
    - all containers
    - all container images
    - docker network that it has created while setting up your environment.

---

## Extras

- The system is implemented using a queuing system (rabbitmq). This allows for a more robust and fault tolerant system as rabbitmq can queue the messages until the listener becomes available.
- For sake of simplicity the system in its current execution form displays all sent messgesy first followed by the received messages. Although the system can be easily be used like a real time system where the receiver can display the messages as soon as it has received ( using 2 terminals to simulate sender and receiver separately) as mentioned before.
