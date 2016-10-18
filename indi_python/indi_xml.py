#!/usr/bin/env python
"""

An implementation of the INDI protocol - Copyright 2003-2007 Elwood Charles Downey

This module does 3 things:

(1) Given some XML as a string it will generate an object that
    represents the XML. This object has methods that can be
    used to inspect and manipulate the text and attributes of
    the XML represented by this object.

(2) Provide functions that generate the same objects as (1)
    given the appropriate arguments.

(3) Given an object created via (1) or (2) return it's
    corresponding XML string.

"""

import numbers
from xml.etree import ElementTree


class IndiXMLException(Exception):
    pass


indi_dict = {}


#
# Decorators.
#
def indiMessage(indi_name, indi_class):
    """
    ...
    """
    global indi_dict
    indi_dict[indi_name] = indi_class
    def decorator(function):
        def wrapper(*args, **kwargs):
            wrapper.actual_kwargs = kwargs
            wrapper.indi_name = indi_name
            wrapper.indi_class = indi_class
            return function(*args, **kwargs)
        return wrapper
    return decorator
    

def requires(required_kwargs):
    """
    This checks that we got values for all the required keywords.
    """
    def decorator(function):
        def wrapper(*args, **kwargs):
            for elt in required_kwargs:
                if not elt in kwargs:
                    raise IndiXMLException("Required argument " + elt + " not specified")
            return function(*args, **kwargs)
        return wrapper
    return decorator


#
# Classes
#
class INDIBase(object):
    """
    INDI object base classes.
    """
    def __init__(self, etype):
        self.etype = etype
        self.attr = {}
                
    def addAttr(self, name, value):
        self.attr[name] = value

    def delAttr(self, name):
        self.attr.pop(name)
        
    def getAttr(self, name):
        return self.attr[name]

    def setAttr(self, name, value):
        self.attr[name] = value

    def toXML(self):
        xml = ElementTree.Element(self.etype)

        # Add attributes.
        for key in self.attr:

            #
            # Avoid Python keywords..
            #
            if (key == "iformat"):
                xml.set("format", str(self.attr[key]))
            else:
                xml.set(key, str(self.attr[key]))

        return xml


class INDIElement(INDIBase):
    """
    INDI element base class.
    """
    def __init__(self, etype, value, kwargs = None, xml = None):
        INDIBase.__init__(self, etype)
        self.value = value
        
        if kwargs is not None:
            for arg in kwargs:
                self.addAttr(arg, kwargs[arg])
        elif xml is not None:
            pass
        else:
            raise IndiXMLException("Dictionary of arguments or XML required.")

    def getValue(self):
        return self.value

    def setValue(self, value):
        self.value = value
        
    def toXML(self):
        xml = INDIBase.toXML(self)
        xml.text = str(self.value)
        return xml


class OneText(INDIElement):
    pass

class OneNumber(INDIElement):
    pass

class OneSwitch(INDIElement):
    pass

class OneBLOB(INDIElement):
    pass


def checkNumber(value):
    #
    # FIXME:
    #    Need to also handle sexagesimal.
    #
    if not isinstance(value, numbers.Number):
        raise IndiXMLException(str(value) + " is not a valid number.")
    return value

def checkSwitch(value):
    if isinstance(value, bool):
        if value:
            value = "On"
        else:
            value = "Off"
    if not value.lower() in ["on", "off"]:
        raise IndiXMLException(value + " is not a valid switch state.")
    return value


#
# Elements describing a vector member value, used in both directions.
#
@indiMessage("oneText", OneText)
@requires(["name"])
def oneText(value, name = None):
    return oneText.indi_class(oneText.indi_name, value, oneText.actual_kwargs)

@indiMessage("oneNumber", OneNumber)
@requires(["name"])
def oneNumber(value, name = None):
    value = checkNumber(value)
    return oneNumber.indi_class(oneNumber.indi_name, value, oneNumber.actual_kwargs)

@indiMessage("oneSwitch", OneSwitch)
@requires(["name"])
def oneSwitch(value, name = None):
    value = checkSwitch(value)
    return oneSwitch.indi_class(oneSwitch.indi_name, value, oneSwitch.actual_kwargs)

@indiMessage("oneBLOB", OneBLOB)
@requires(["name", "size", "iformat"])
def oneBLOB(value, name = None, size = None, iformat = None):
    return oneBLOB.indi_class(oneBLOB.indi_name, value, oneBLOB.actual_kwargs)


#
# Simple tests.
#
if (__name__ == "__main__"):
    print ElementTree.tostring(oneText("One", name = "py").toXML(), 'utf-8')
    print indi_dict


