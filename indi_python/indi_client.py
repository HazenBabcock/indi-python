#!/usr/bin/env python
"""

A PyQt5 (client) interface to an INDI server. This will only work
in the context of a PyQt application.

"""

from xml.etree import ElementTree
from PyQt5 import QtCore, QtNetwork


import indi_python.indi_xml as indiXML


class INDIClient(QtCore.QObject):
    received = QtCore.pyqtSignal(object) # Received messages as INDI Python objects.

    def __init__(self,
                 address = QtNetwork.QHostAddress(QtNetwork.QHostAddress.LocalHost),
                 port = 7624,
                 verbose = True,
                 parent = None):
        QtCore.QObject.__init__(self)
        self.message_string = ""
        self.verbose = verbose

        # Create socket.
        self.socket = QtNetwork.QTcpSocket()
        self.socket.disconnected.connect(self.handleDisconnect)
        self.socket.readyRead.connect(self.handleReadyRead)

        # Connect to socket.
        self.socket.connectToHost(address, port)

    def disconnect(self):
        if self.socket is not None:
            self.socket.disconnectFromHost()
            
    def handleDisconnect(self):
        self.socket = None

    def handleReadyRead(self):

        # Add starting tag if this is new message.
        if (len(self.message_string) == 0):
            self.message_string = "<data>"
            
        # Get message from socket.
        while self.socket.bytesAvailable():
            self.message_string += str(self.socket.read(1000000))

        # Add closing tag.
        self.message_string += "</data>"

        # Try and parse the message.
        try:
            if self.verbose:
                print("INDIClient: message length " + str(len(self.message_string)) + "bytes.")
            messages = ElementTree.fromstring(self.message_string)
            self.message_string = ""
            for message in messages:
                self.received.emit(indiXML.parseETree(message))

        # Message is incomplete, remove </data> and wait..
        except ElementTree.ParseError:
            if self.verbose:
                print("INDIClient: message is not yet complete.")
            self.message_string = self.message_string[:-7]

    def send(self, indi_command):
        if self.socket is not None:
            self.socket.write(indi_command.toXML() + "\n")


if (__name__ == "__main__"):

    import sys
    import time
    
    from PyQt5 import QtWidgets

    
    class Widget(QtWidgets.QWidget):

        def __init__(self):
            QtWidgets.QWidget.__init__(self)

            self.client = INDIClient()
            self.client.received.connect(self.handleReceived)

        def handleReceived(self, message):
            print(message)

        def send(self, message):
            self.client.send(message)

    app = QtWidgets.QApplication(sys.argv)
    widget = Widget()
    widget.show()

    # Get a list of devices.
    widget.send(indiXML.clientGetProperties(indi_attr = {"version" : "1.0"}))
    time.sleep(1)

    # Connect to the CCD simulator.
    widget.send(indiXML.newSwitchVector([indiXML.oneSwitch("On", indi_attr = {"name" : "CONNECT"})],
                                        indi_attr = {"name" : "CONNECTION", "device" : "CCD Simulator"}))
    time.sleep(1)

    # Enable BLOB mode.
    widget.send(indiXML.enableBLOB("Also", indi_attr = {"device" : "CCD Simulator"}))
    time.sleep(1)

    # Request image.
    widget.send(indiXML.newNumberVector([indiXML.oneNumber(1, indi_attr = {"name" : "CCD_EXPOSURE_VALUE"})],
                                        indi_attr = {"name" : "CCD_EXPOSURE", "device" : "CCD Simulator"}))
    time.sleep(1)
    
    sys.exit(app.exec_())
