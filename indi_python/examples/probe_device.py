#!/usr/bin/env python
"""
Contact the requested device and get all of it's properties.

Hazen 02/17
"""

import argparse
import time

import indi_python.basic_indi_client as basicIndiClient
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

# Create client.
timeout = 0.5
bic = basicIndiClient.BasicIndiClient(args.ipaddress, args.port, timeout)

# Query device
bic.sendMessage(indiXML.clientGetProperties(indi_attr = {"version" : "1.0", "device" : args.device}))
time.sleep(timeout)

# Connect to user requested device.
bic.sendMessage(indiXML.newSwitchVector([indiXML.oneSwitch("On", indi_attr = {"name" : "CONNECT"})],
                                        indi_attr = {"name" : "CONNECTION", "device" : args.device}))
time.sleep(timeout)

# Get all the XML that was sent in response to the above.
messages = bic.waitMessages()

# Print the messages.
for message in messages:
    print(message)

# Close the connection.
bic.close()
