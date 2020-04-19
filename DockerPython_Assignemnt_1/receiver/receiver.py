#!/usr/bin/python

"""
    Container2Container File Transfer : receiver.py
    ------------------------------------------------------------------------------------------
    This script does the work of :
        - receiving encrypted data from rabbitmq queue
        - decrypt it
        - store it in xml file at location `/xmls/`

    Script uses the default user of rabbitmq. For decryption, script uses the cryptography.fernet package.
"""

from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from json import dumps, loads
from sys import exit
from cryptography.fernet import Fernet


def pikaconnect():
    """
    Function to create a pika blocking connection
    :param: None
    :return: pika connection
    """
    try:
        connection = BlockingConnection(ConnectionParameters("rabbitqueue", 5672, "/", PlainCredentials("guest","guest")))
        channel = connection.channel()
        return channel
    except Exception as e:
        print("Connection Failed : Reason : {}".format(str(e)))


def decrypt_data(encrypted_data):
    """
    Function to decrypt the xml data
    :param: encrypted xml string
    :return: decrypted xml string
    """
    key = 'xAboLHTvnE8bjx2Kp_neueda_6RnrE2FkanRQjAjjK8='
    f = Fernet(key)
    return f.decrypt(encrypted_data.encode()).decode()


def process_message(channel, method, properties, body):
    """
    Callback Function that listens to rabbitqueue for any new message
    :param: channel
    :param: method
    :param: properties
    :param: body
    :return: None
    """
    json_data = loads(body)
    if str(json_data["metadata-filename"]) == "done" and str(json_data["data"]) == "exit":
        print("\n\n - Received Exit signal... Exiting...!")
        exit(0)

    print("\n\n - Processing encrypted data :", json_data['data'])
    decrypted_xml = decrypt_data(str(json_data["data"]))
    print("\n\t Decrypted data :", decrypted_xml)

    with open("/xmls/" + str(json_data['metadata-filename']).split(".")[0] + ".xml","w") as ftw:
        ftw.write(decrypted_xml)
    print("\n\t File successfully created at location /xmls/{}.xml".format(str(json_data['metadata-filename']).split(".")[0]))

    print("\n\t ------------- Data received -------------")

# Main function
def main():
    try:
        pika_connection = pikaconnect()

        pika_connection.basic_consume(process_message, queue='data-queue', no_ack=True)

        print('Waiting for data... To exit press CTRL+C')
        pika_connection.start_consuming()

    except Exception as e:
        print("Error occured : {}".format(str(e)))
    finally:
        pika_connection.close()

if __name__ == "__main__":
    main()
