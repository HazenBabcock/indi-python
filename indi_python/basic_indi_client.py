#!/usr/bin/env python
"""
A basic INDI client.

Hazen 02/17
"""

import argparse
import socket
import sys
import time
from xml.etree import ElementTree

import indi_python.indi_xml as indiXML


class BasicIndiClient(object):

    def __init__(self, ip_address, port, timeout = 0.5):
        socket.setdefaulttimeout(timeout)

        self.a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.a_socket.connect((ip_address, port))

        self.device = None
        self.message_string = None

    def close(self):
        self.a_socket.close()

    def getMessages(self):
        """
        This will return 'None' if there were no messages, or no complete 
        messages. The expectation is that this will then be called again 
        after some timeout to get the rest of message.
        """
        # Add starting tag if this is a new message.
        if self.message_string is None:
            self.message_string = "<data>"

        # Get as much data as we can from the socket.
        try:
            while True:
                response = self.a_socket.recv(2**20)
                self.message_string += response.decode("latin1")
        except socket.timeout:
            pass

        # Add closing tag.
        self.message_string += "</data>"

        # Try and parse the message.
        messages = None
        try:
            etree_messages = ElementTree.fromstring(self.message_string)
            self.message_string = None
            messages = []
            for etree_message in etree_messages:
                xml_message = indiXML.parseETree(etree_message)

                # Filter message is self.device is not None.
                if self.device is not None:
                    if (self.device == xml_message.getAttr("device")):
                        messages.append(xml_message)

                # Otherwise just keep them all.
                else:
                    messages.append(xml_message)

        # Reset if the message could not be parsed.
        except ElementTree.ParseError:
            self.message_string = self.message_string[:-len("</data>")]

        return messages

    def sendMessage(self, indi_elt):
        self.a_socket.send(indi_elt.toXML() + b'\n')

    def setDevice(self, device = None):
        self.device = device
        
    def waitMessages(self):
        """
        This will block until all messages are recieved.

        FIXME: Add maximum wait time / attempts?
        """
        messages = self.getMessages()
        while messages is None:
            time.sleep(self.timeout)
            messages = self.getMessages()
        return messages
