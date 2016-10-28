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
                 parent = None):
        QtCore.QObject.__init__(self)

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

        # Get message from socket.
        message_string = "<data>"
        while self.socket.canReadLine():
            message_string += str(self.socket.readLine())
        message_string += "</data>"

        messages = ElementTree.fromstring(message_string)
        for message in messages:
            print(indiXML.parseETree(message))
            #self.received.emit(indi_xml.parseETree(message))

    def send(self, indi_command):
        if self.socket is not None:
            self.socket.write(indi_command.toXML() + "\n")


if (__name__ == "__main__"):

    import sys
    
    from PyQt5 import QtWidgets

    
    class Widget(QtWidgets.QWidget):

        def __init__(self):
            QtWidgets.QWidget.__init__(self)

            self.client = INDIClient()
            self.client.received.connect(self.handleReceived)

        def handleReceived(self, message):
            pass
            #self.close()

        def send(self, message):
            self.client.send(message)

    app = QtWidgets.QApplication(sys.argv)
    widget = Widget()
    widget.show()
    widget.send(indiXML.clientGetProperties(indi_attr = {"version" : "1.0"}))
    sys.exit(app.exec_())
