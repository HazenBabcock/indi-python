#!/usr/bin/env python
"""
A basic INDI client.

Hazen 02/17
"""

import argparse
import sys
import telnetlib
import time
from xml.etree import ElementTree

import indi_python.indi_xml as indiXML


class BasicIndiClient(object):

    def __init__(self, ip_address, port, timeout = 0.5):
        self.connection = telnetlib.Telnet(ip_address, port, timeout)
        self.timeout = timeout
        
        self.message_string = None

    def close(self):
        self.connection.close()
        
    def getMessages(self, timeout = None):
        if timeout is None:
            timeout = self.timeout

        # Add starting tag if this is a new message.
        if self.message_string is None:
            self.message_string = "<data>"

        # Get available bytes from socket.
        response = self.connection.read_until(b"!-#-!-#-!", timeout)
        self.message_string += response.decode("latin1")

        # Add closing tag.
        self.message_string += "</data>"

        # Try and parse the message.
        messages = None
        try:
            etree_messages = ElementTree.fromstring(self.message_string)
            self.message_string = None
            messages = []
            for etree_message in etree_messages:
                messages.append(indiXML.parseETree(etree_message))

        except ElementTree.ParseError:
            self.message_string = self.message_string[:-len("</data>")]

        return messages

    def sendMessage(self, indi_elt):
        self.connection.write(indi_elt.toXML() + b'\n')


