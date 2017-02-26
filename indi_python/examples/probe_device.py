#!/usr/bin/env python
"""
Contact the requested device and get all of it's properties.

Hazen 02/17
"""

import argparse
import sys
import telnetlib
import time
from xml.etree import ElementTree

import indi_python.indi_xml as indiXML


# Parse command line arguments.

parser = argparse.ArgumentParser(description = 'Queries indiserver to get all the properties of a device')

parser.add_argument('--device', dest='device', type=str, required=True,
                    help = "The name of the device to probe, such as 'Telescope Simulator'")
parser.add_argument('--ip', dest='ipaddress', type=str, required=False, default="127.0.0.1",
                    help = "The IP address of the INDI server.")
parser.add_argument('--port', dest='port', type=int, required=False, default=7624,
                    help = "The port of the INDI server.")
                                 
args = parser.parse_args()

# Open telnet connection.
timeout = 0.5
conn = telnetlib.Telnet(args.ipaddress, args.port, timeout)

# Query device
conn.write(indiXML.clientGetProperties(indi_attr = {"version" : "1.0", "device" : args.device}).toXML() + b'\n')
time.sleep(timeout)

# Connect to user requested device.
conn.write(indiXML.newSwitchVector([indiXML.oneSwitch("On", indi_attr = {"name" : "CONNECT"})],
                                   indi_attr = {"name" : "CONNECTION", "device" : args.device}).toXML() + b'\n')
time.sleep(timeout)

# Get all the XML that was sent in response to the above.
xml_string = "<messages>"
response = conn.read_until(b"asdf", timeout)
while response:
    response = response.decode("latin1")
    xml_string += response
    response = conn.read_until(b"asdf", timeout)
xml_string += "</messages>"

conn.close()

# Parse the XML into INDI objects and print the objects.
messages = ElementTree.fromstring(xml_string)
for message in messages:
    print(indiXML.parseETree(message))
    
