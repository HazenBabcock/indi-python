#!/usr/bin/env python
"""
Capture a single image from the requested (Camera) device.

Hazen 02/17
"""

import argparse
import fitsio
import numpy
import os
import time
from xml.etree import ElementTree

import indi_python.basic_indi_client as basicIndiClient
import indi_python.indi_xml as indiXML
import indi_python.simple_fits as simpleFits


# Parse command line arguments.

parser = argparse.ArgumentParser(description = 'Captures a single image from a Camera')

parser.add_argument('--camera', dest='camera', type=str, required=True,
                    help = "The name of the camera device")
parser.add_argument('--exptime', dest='exptime', type=float, required=False, default="0.1",
                    help = "The exposure time in seconds.")
parser.add_argument('--fits', dest='fits', type=str, required=False, default="capture.fits",
                    help = "The name of FITS file to save the result in.")
parser.add_argument('--ip', dest='ipaddress', type=str, required=False, default="127.0.0.1",
                    help = "The IP address of the INDI server.")
parser.add_argument('--port', dest='port', type=int, required=False, default=7624,
                    help = "The port of the INDI server.")

                                 
args = parser.parse_args()

# Create client.
timeout = 0.5
bic = basicIndiClient.BasicIndiClient(args.ipaddress, args.port, timeout = timeout)

# Connect to user requested camera and enable BLOB mode.
bic.sendMessage(indiXML.newSwitchVector([indiXML.oneSwitch("On", indi_attr = {"name" : "CONNECT"})],
                                        indi_attr = {"name" : "CONNECTION", "device" : args.camera}))
bic.sendMessage(indiXML.enableBLOB("Also", indi_attr = {"device" : args.camera}))
time.sleep(timeout)

# With 'GPhoto CCD' we need to probe to get the image size.
if (args.camera == "GPhoto CCD"):
    print("Sending initial dummy values for camera info.")
    bic.sendMessage(indiXML.newNumberVector([indiXML.oneNumber(1000, indi_attr = {"name" : "CCD_MAX_X"}),
                                             indiXML.oneNumber(1000, indi_attr = {"name" : "CCD_MAX_Y"}),
                                             indiXML.oneNumber(1, indi_attr = {"name" : "CCD_PIXEL_SIZE"}),
                                             indiXML.oneNumber(1, indi_attr = {"name" : "CCD_PIXEL_SIZE_X"}),
                                             indiXML.oneNumber(1, indi_attr = {"name" : "CCD_PIXEL_SIZE_Y"}),
                                             indiXML.oneNumber(16, indi_attr = {"name" : "CCD_BITSPERPIXEL"})],
                                            indi_attr = {"name" : "CCD_INFO", "device" : args.camera}))
    time.sleep(timeout)

# Request a picture.
print("Starting capture")
bic.sendMessage(indiXML.newNumberVector([indiXML.oneNumber(args.exptime, indi_attr = {"name" : "CCD_EXPOSURE_VALUE"})],
                                        indi_attr = {"name" : "CCD_EXPOSURE", "device" : args.camera}))
time.sleep(timeout)

# Wait for image.
print("Waiting for image")
np_image = None
while True:
    messages = bic.waitMessages()
    for message in messages:
        if isinstance(message, indiXML.SetBLOBVector):
            np_image = simpleFits.FitsImage(fits_string = message.getElt(0).getValue()).getImage().astype(numpy.uint16)
    if np_image is not None:
        break

# Save the image.
fitsio.write(args.fits, np_image, clobber = True)

# Close the connection.
bic.close()
