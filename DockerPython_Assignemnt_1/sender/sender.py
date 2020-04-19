#!/usr/bin/python3

"""
    Container2Container File Transfer : sender.py
    ------------------------------------------------------------------------------------------
    This script does the work of :
        - reading json files from `/jsons` location
        - validating it
        - converting it to xml
        - encrypting it
        - pushing it to rabbitmq queue.

    For converting to xml, the script has two options :
        - Convert using dicttoxml python library [ Code commented on line 91,92 ]
        - Convert using custom implementation [ Default ]

    If user wants to use method 1 [ dicttoxml ], they can uncomment the 2 lines [91,92] in convert_to_xml()
    method and rebuild the docker image if already built.

    Script uses the default user of rabbitmq. For encryption, script uses the cryptography.fernet package.
"""

from pika import BlockingConnection, ConnectionParameters, PlainCredentials, BasicProperties
from json import dumps, loads
from os import listdir
from sys import exit
from cryptography.fernet import Fernet

# helper functions
def _value_converter(xml, value):
    """
    Recursive helper function which will convert values for xml
    :param: empty xml
    :param: value
    :return: xml converted values
    """
    if isinstance(value, int) or isinstance(value, float):
        xml += str(value)
    else:
        if isinstance(value, str):
            xml += value
        elif isinstance(value, list) or isinstance(value, tuple):
            for each in value:
                xml += '<item>'
                xml = _value_converter(xml, each)
                xml += '</item>'
        elif isinstance(value, dict):
            for value_key, value_value in value.items():
                xml += '<' + value_key + '>'
                xml = _value_converter(xml, value_value)
                xml += '</' + value_key + '>'
    return xml


# proper functions
def pikaconnect():
    """
    Function to create a pika blocking connection
    :param: None
    :return: pika connection
    """
    try:
        connection = BlockingConnection(ConnectionParameters("rabbitqueue", 5672, "/", PlainCredentials("guest","guest")))
        channel = connection.channel() 
        channel.queue_declare(queue='data-queue', durable=True)
        return channel
    except Exception as e:
        print("Connection Failed : Reason : {}".format(str(e)))


def push_data_to_queue(pika_connection, filename, encrypted_data):
    """
    Function to push data to rabbitmq queue
    :param: pika_connection
    :param: filename
    :param: encrypted_data
    :return: None
    """
    pika_connection.basic_publish(exchange='',
            routing_key='data-queue',
            body=dumps({"metadata-filename":filename,"data":encrypted_data}),
            properties=BasicProperties(delivery_mode = 2 ))


def convert_to_xml(json_data):
    """
    Function to convert Json to XML
    :param: json_data
    :return: converted XML

    uncomment first 2 lines to use dicttoxml method instead of custom implementation
    """
    #from dicttoxml import dicttoxml
    #return dicttoxml(json_data)
    
    xml = "<root>"
    for key,value in json_data.items():
        xml += "<" + key + ">"
        xml = _value_converter(xml, value)
        xml += "</" + key + ">"
    xml += "</root>"
    return xml


def encrypt_xml(xml):
    """
    Function to encrypt the xml data
    :param: xml
    :return: encrypted xml string
    """

    key = 'xAboLHTvnE8bjx2Kp_neueda_6RnrE2FkanRQjAjjK8='
    f = Fernet(key)
    return f.encrypt(xml.encode()).decode()

# main function
def main():
    try:
        pika_connection = None
        # get list of '.json' files to transfer from the /jsons/ dir
        files_to_transfer = lambda filename: filename[-5:] == '.json', listdir("jsons/")
        print("FTT : {}".format(files_to_transfer))
        print("\n # There are Total {} file(s) to transfer".format(str(len(files_to_transfer[1]))))
        
        if not files_to_transfer:
            print("No .json to process... Exiting...")
            exit(0)

        # make a pika connection
        pika_connection = pikaconnect()

        # for each file to transfer, read json, convert it to xml, encrypt it and push it to the queue
        for file_to_transfer in files_to_transfer[1]:
            print("\n\n - Processing file : {}".format(str(file_to_transfer)))

            # read json data
            with open("/jsons/" + file_to_transfer, "r") as ftt:
                file_content = ftt.read()
            try:
                file_content = dumps(loads(file_content))
            except ValueError as ve:
                print("\t!!! Unable to parse filedata, json expected !!!")
                continue

            print("\tContent of the file: {}".format(file_content))

            # convert data to xml
            xml = convert_to_xml(loads(file_content))
            print("\n\tConverted xml: {}".format(xml))

            # encrypt the xml
            encrypted_xml = encrypt_xml(str(xml))
            print("\n\tEncrypted xml: {}".format(encrypted_xml))

            # push the data to queue
            push_data_to_queue(pika_connection, file_to_transfer, encrypted_xml)
            print("\n\t------------- Data sent -------------")

        # push special flag to indicate eof
        push_data_to_queue(pika_connection, "done", "exit")
        print("\n\t------------- Sent exit signal -------------")

    except Exception as e:
        print("Error occured : {}".format(str(e)))

    finally:

        # gracefully close pika connection if any open
        if pika_connection != None:
            pika_connection.close()


if __name__ == "__main__":
    main()
