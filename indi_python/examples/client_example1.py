#!/usr/bin/env python
"""
Simple example of the use of the indi-python library as a client.

Hazen 11/16
"""

import astropy.coordinates
import astropy.units
import numpy
import os
import sys

from PyQt5 import QtCore, QtGui, QtWidgets

import indi_python.indi_xml as indiXML
import indi_python.indi_client as indiClient
import indi_python.simple_fits as simpleFits

import client_example1_ui as clientExample1Ui


class CameraDisplayWidget(QtWidgets.QWidget):

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)

        self.im_min = None
        self.im_max = None
        self.mag_index = 2
        self.mags = [0.25, 0.5, 1.0, 2.0, 4.0]
        self.numpy_image = None
        self.qt_image = None

    def newImage(self, numpy_image, im_min, im_max):
        self.numpy_image = numpy_image.astype(numpy.float32)
        self.rescaleImage(im_min, im_max)

    def paintEvent(self, event):
        if self.qt_image is not None:
            painter = QtGui.QPainter(self)

            # Draw image.
            painter.drawImage(0, 0, self.qt_image)

    def redrawImage(self):
        if self.numpy_image is not None:

            # Scale the image.
            temp_image = self.numpy_image - self.im_min
            temp_image = temp_image * 255.0/(self.im_max - self.im_min)
            temp_image[(temp_image < 0.0)] = 0.0
            temp_image[(temp_image > 255.0)] = 255.0
            temp_image = temp_image.astype(numpy.uint8)

            # Create a QT version of the image.
            self.qt_image = QtGui.QImage(temp_image.data,
                                         temp_image.shape[1],
                                         temp_image.shape[0],
                                         QtGui.QImage.Format_Indexed8)
            self.qt_image.ndarray = temp_image
            for i in range(256):
                self.qt_image.setColor(i,QtGui.qRgb(i,i,i))

            # Resize image.
            mag_factor = self.mags[self.mag_index]
            if (mag_factor != 1.0):
                new_width = int(mag_factor * self.qt_image.width())
                new_height = int(mag_factor * self.qt_image.height())
                self.qt_image = self.qt_image.scaled(new_width, new_height)

            self.setFixedSize(self.qt_image.width(), self.qt_image.height())
            self.update()

    def rescaleImage(self, im_min, im_max):
        self.im_min = float(im_min)
        self.im_max = float(im_max)
        if (self.im_max < self.im_min):
            self.im_max = self.im_min + 1
        self.redrawImage()
        
    def wheelEvent(self, event):
        if (event.angleDelta().y() > 0):
            self.mag_index += 1
            if (self.mag_index == len(self.mags)):
                self.mag_index = len(self.mags) - 1
        else:
            self.mag_index -= 1
            if (self.mag_index < 0):
                self.mag_index = 0
        self.redrawImage()

            
class Window(QtWidgets.QMainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)

        self.cur_dec = "00:00:00"
        self.cur_ra = "00:00:00"
        self.moving_timer = QtCore.QTimer()
        self.settings = QtCore.QSettings("client_example1", "indi_python")

        self.moving_timer.setSingleShot(True)
        self.moving_timer.setInterval(1500)
        
        # Configure UI.
        self.ui = clientExample1Ui.Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.rangeSlider.setRange([0, 1000, 1])

        # Assume the mount is not to our initial RA, Dec.
        self.ui.decLineEdit.setStyleSheet("QLineEdit { background : yellow; }")
        self.ui.raLineEdit.setStyleSheet("QLineEdit { background : yellow; }")
            
        # Configure display
        self.camera_display_widget = CameraDisplayWidget(self)
        self.ui.cameraScrollArea.setWidget(self.camera_display_widget)
        
        # Load settings
        self.resize(self.settings.value("MainWindow/Size", self.size()))
        self.move(self.settings.value("MainWindow/Position", self.pos()))
        self.cur_dec = self.settings.value("dec", self.cur_dec)
        self.ui.decLineEdit.setText(self.cur_dec)
        self.cur_ra = self.settings.value("ra", self.cur_ra)
        self.ui.raLineEdit.setText(self.cur_ra)                
        
        # Connect signals.
        self.moving_timer.timeout.connect(self.handleStabilized)
        
        self.ui.actionQuit.triggered.connect(self.handleQuit)
        self.ui.capturePushButton.clicked.connect(self.handleCapture)
        self.ui.decLineEdit.textEdited.connect(self.handleDecTextEdited)
        self.ui.gotoPushButton.clicked.connect(self.handleGoTo)
        self.ui.raLineEdit.textEdited.connect(self.handleRaTextEdited)
        self.ui.rangeSlider.rangeChanged.connect(self.handleRangeChange)

        range_max = int(self.settings.value("range_max", 200))

        self.ui.rangeSlider.setValues([int(self.settings.value("range_min", 0)), range_max])

        # Connect a (local) indiserver.
        self.indi_client = indiClient.INDIClient(parent = self)
        self.indi_client.received.connect(self.handleReceived)

        # Open connection to the CCD simulator and enable BLOB mode.
        self.indi_client.send(indiXML.newSwitchVector([indiXML.oneSwitch("On", indi_attr = {"name" : "CONNECT"})],
                                                      indi_attr = {"name" : "CONNECTION", "device" : "CCD Simulator"}))
        self.indi_client.send(indiXML.enableBLOB("Also", indi_attr = {"device" : "CCD Simulator"}))

        # Open connection to the Telescope simulator.
        self.indi_client.send(indiXML.newSwitchVector([indiXML.oneSwitch("On", indi_attr = {"name" : "CONNECT"})],
                                                      indi_attr = {"name" : "CONNECTION", "device" : "Telescope Simulator"}))

        # Change telescope focal length. The aperture parameters does not appear to actually do anything.
        self.indi_client.send(indiXML.newNumberVector([indiXML.oneNumber(300.0, indi_attr = {"name" : "TELESCOPE_APERTURE"}),
                                                       indiXML.oneNumber(300.0, indi_attr = {"name" : "TELESCOPE_FOCAL_LENGTH"})],
                                                      indi_attr = {"name" : "TELESCOPE_INFO", "device" : "Telescope Simulator"}))

    def closeEvent(self, event):
        self.settings.setValue("MainWindow/Size", self.size())
        self.settings.setValue("MainWindow/Position", self.pos())

        self.settings.setValue("dec", self.cur_dec)
        self.settings.setValue("ra", self.cur_ra)
        self.settings.setValue("range_max", self.ui.rangeMaxLabel.text())
        self.settings.setValue("range_min", self.ui.rangeMinLabel.text())

    def handleCapture(self, boolean):
        # Start capture.
        exp_time = float(self.ui.exposureTimeDoubleSpinBox.value())
        self.indi_client.send(indiXML.newNumberVector([indiXML.oneNumber(exp_time, indi_attr = {"name" : "CCD_EXPOSURE_VALUE"})],
                                                      indi_attr = {"name" : "CCD_EXPOSURE", "device" : "CCD Simulator"}))
        self.ui.capturePushButton.setEnabled(False)

    def handleDecTextEdited(self, new_text):
        try:
            angle = astropy.coordinates.Angle(new_text, unit = astropy.units.deg)
        except ValueError:
            self.ui.decLineEdit.setStyleSheet("QLineEdit { background : red; }")
        else:
            self.ui.decLineEdit.setStyleSheet("QLineEdit { background : yellow; }")
            self.cur_dec = angle.to_string(sep=":")

    def handleGoTo(self, boolean):
        # Update where the telescope is pointed.
        self.indi_client.send(indiXML.newNumberVector([indiXML.oneNumber(self.cur_dec, indi_attr = {"name" : "DEC"}),
                                                       indiXML.oneNumber(self.cur_ra, indi_attr = {"name" : "RA"})],
                                                      indi_attr = {"name" : "EQUATORIAL_EOD_COORD", "device" : "Telescope Simulator"}))
        self.ui.gotoPushButton.setEnabled(False)

        # Start moving timer. When this times out we assume that the mount
        # has stabilized. Note that this timer gets restarted each time we
        # get an updated position from the mount.
        self.moving_timer.start()
        
    def handleRaTextEdited(self, new_text):
        try:
            angle = astropy.coordinates.Angle(new_text, unit = astropy.units.deg)
        except ValueError:
            self.ui.raLineEdit.setStyleSheet("QLineEdit { background : red; }")
        else:
            self.ui.raLineEdit.setStyleSheet("QLineEdit { background : yellow; }")
            self.cur_ra = angle.to_string(sep=":")

    def handleReceived(self, message):
        print(message)
        
        # Check for image BLOB from CCD1.
        if isinstance(message, indiXML.SetBLOBVector) and (message.getAttr("name") == "CCD1"):
            if isinstance(message.getElt(0), indiXML.OneBLOB):
                np_image = simpleFits.FitsImage(fits_string = message.getElt(0).getValue()).getImage()
                im_min = int(self.ui.rangeMinLabel.text())
                im_max = int(self.ui.rangeMaxLabel.text())
                self.camera_display_widget.newImage(np_image, im_min, im_max)
                return

        # Check for updated exposure time form CCD1.
        if isinstance(message, indiXML.SetNumberVector) and (message.getAttr("name") == "CCD_EXPOSURE"):
            remaining_time = float(message.getElt(0).getValue())
            if (remaining_time == 0.0):
                self.ui.capturePushButton.setText("Capture")
                self.ui.capturePushButton.setEnabled(True)
            else:
                self.ui.capturePushButton.setText("{0:.1f}".format(remaining_time))
            return

        # Check for updated position.
        if isinstance(message, indiXML.SetNumberVector) and (message.getAttr("name") == "EQUATORIAL_EOD_COORD"):
            self.moving_timer.start()
            mount_ra = astropy.coordinates.Angle(float(message.getElt(0).getValue()), unit = astropy.units.deg)
            self.cur_ra = mount_ra.to_string(sep=":")
            self.ui.raLineEdit.setText(self.cur_ra)
            
            mount_dec = astropy.coordinates.Angle(float(message.getElt(1).getValue()), unit = astropy.units.deg)
            self.cur_dec = mount_dec.to_string(sep=":")
            self.ui.decLineEdit.setText(self.cur_dec)

    def handleStabilized(self):
        self.ui.decLineEdit.setStyleSheet("QLineEdit { background : white; }")
        self.ui.raLineEdit.setStyleSheet("QLineEdit { background : white; }")
        self.ui.gotoPushButton.setEnabled(True)

    def handleQuit(self, boolean):
        self.close()

    def handleRangeChange(self, im_min, im_max):
        im_min = int(im_min)
        im_max = int(im_max)
        self.ui.rangeMinLabel.setText(str(im_min))
        self.ui.rangeMaxLabel.setText(str(im_max))
        self.camera_display_widget.rescaleImage(im_min, im_max)

        
if (__name__ == '__main__'):

    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
