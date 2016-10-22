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

Notes:
 (1) To avoid Python keywords the following correspondence is used:
       'iformat' - 'format'
       'imin' - 'min'
       'imax' - 'max'

 (2) There are two forms of getProperties, deviceGetProperties() and clientGetProperties().

"""

import numbers
from xml.etree import ElementTree


class IndiXMLException(Exception):
    pass


class INDIBase(object):
    """
    INDI object base classes.
    """
    def __init__(self, etype, value, kwargs, xml):
        self.etype = etype
        self.attr = {}

        if kwargs is not None:
            for arg in kwargs:
                self.addAttr(arg, kwargs[arg])
        elif xml is not None:
            pass
        else:
            raise IndiXMLException("Dictionary of arguments or XML required.")
        
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
    def __init__(self, etype, value, kwargs, xml):
        INDIBase.__init__(self, etype, value, kwargs, xml)
        self.value = value
        
    def getValue(self):
        return self.value

    def setValue(self, value):
        self.value = value
        
    def toXML(self):
        xml = INDIBase.toXML(self)
        xml.text = str(self.value)
        return xml

    
class INDIVector(INDIBase):
    """
    INDI vector base class.
    """
    def __init__(self, etype, alist, kwargs, xml):
        INDIBase.__init__(self, etype, value, kwargs, xml)
        self.elt_list = eltlist
        
        if kwargs is not None:
            for arg in kwargs:
                self.addAttr(arg, kwargs[arg])
        elif xml is not None:
            pass
        else:
            raise IndiXMLException("Dictionary of arguments or XML required.")


#
# Validator functions.
#

def groupTag(value):
    return value

def labelValue(value):
    return value

def listValue(value):
    return value

def nameValue(value):
    return value

def numberValue(value):
    #
    # FIXME:
    #    Need to also handle sexagesimal.
    #
    if not isinstance(value, numbers.Number):
        raise IndiXMLException(str(value) + " is not a valid number.")
    return value

def propertyPerm(value):
    return value

def propertyState(value):
    return value

def switchState(value):
    if isinstance(value, bool):
        if value:
            value = "On"
        else:
            value = "Off"
    if not value.lower() in ["on", "off"]:
        raise IndiXMLException(value + " is not a valid switch state.")
    return value

def timeValue(value):
    return value

def textValue(value):
    return value

        
# This stores the correspondence between Python classes and INDI messages.
indi_dict = {}

#
# The INDI specification.
#
# Notes:
#
# 1. If the class property is not specified it defaults to the specification key
#    with the first letter changed to uppercase (defTextVector -> DefTextVector).
#
# 2. If the xml property is not specified it defaults to the specification key.
#
# 3. The structure of attribute element is [name, xml name (if different), required, validator, documentation].
#
indi_spec = {"clientGetProperties" : {"class" : "GetProperties",
                                      "xml" : "getProperties",
                                      "base" : INDIBase,
                                      "docs" : "Command to enable snooping messages from other devices. Once enabled, defXXX and setXXX messages for the Property with the given name and other messages from the device will be sent to this driver channel. Enables messages from all devices if device is not specified, and all Properties for the given device if name is not specified. Specifying name without device is not defined.",
                                      "attributes" : [["device", None, False, nameValue, "device to snoop, or all if absent"],
                                                      ["name", None, False, nameValue, "property of device to snoop, or all if absent"]]},
             
             "defTextVector" : {"base" : INDIVector,
                                "docs" : "Define a property that holds one or more text elements.",
                                "arg" : listValue,
                                "attributes" : [["device", None, True, nameValue, "Name of Device"],
                                                ["name", None, True, nameValue, "Name of Property"],
                                                ["label", None, False, labelValue, "GUI label, use name by default"],
                                                ["group", None, False, groupTag, "Property group membership, blank by default"],
                                                ["state", None, True, propertyState, "Current state of Property"],
                                                ["perm", None, True, propertyPerm, "Ostensible Client controlability"],
                                                ["timeout", None, False, numberValue, "Worse-case time to affect, 0 default, N/A for ro"],
                                                ["timestamp", None, False, timeValue, "Moment when these data were valid"],
                                                ["message", None, False, textValue, "Commentary"]]},
             }


#
# The API
#

def fromINDIXML(xml):
    pass

def makeINDI(indi_type, indi_arg = None, indi_attributes = None):
    """
    Returns an INDI object of the requested type.

    An ElementTree.Element XML representation of the object can be created by
    calling the objects toXML() method.
    """
    global indi_spec
    
    # Check that the requested type exists.
    if not indi_type in indi_spec:
        raise IndiXMLException(indi_type + " is not a valid INDI XML command type.")

    type_spec = indi_spec[indi_type]

    # Check if an argument was expected.
    if hasattr(type_spec, "arg"):
        if indi_arg is not None:
            raise IndiXMLException(indi_type + " requires an argument.")

        # Check argument with validator function.
        indi_arg = type_spec["arg"](indi_arg)

    elif indi_arg is not None:
        raise IndiXMLException(indi_type + " does not expect an argument.")

    # Check / validate attributes.
    all_attr = []
    final_attr = {}
    for attr in type_spec["attributes"]:
        attr_name = attr[0]
        all_attr.append(attr_name)

        # Check if required.
        if attr[2] and not attr_name in indi_attributes:
            raise IndiXMLException(attr_name + " is a required attribute.")

        # Check if valid.
        if attr_name in indi_attributes:
            if attr[1] is None:
                attr[1] = attr[0]
            final_attr[attr[1]] = attr[3](indi_attributes[attr_name])

    for attr in indi_attributes:
        if not attr in all_attr:
            raise IndiXMLException(attr + " is not an attribute of " + indi_type + ".")

    # Create object.
    if not hasattr(type_spec, "spec_object"):

        # Use (capitalized) XML command name
        if not hasattr(type_spec, "class"):
            type_spec["class"] = indi_type[0].upper() + indi_type[1:]
            
        type_spec["spec_object"] = type(type_spec["class"], (type_spec["base"],), {})

    return type_spec["spec_object"](type_spec["class"], indi_arg, final_attr, None)

#
# Simple tests.
#
if (__name__ == "__main__"):
    gp = makeINDI("clientGetProperties", indi_attributes = {"name" : "bar"})
    print(gp)
    print(ElementTree.tostring(gp.toXML(), 'utf-8'))

    gp.setAttr("name", "baz")
    print(ElementTree.tostring(gp.toXML(), 'utf-8'))

    print(gp.getValue())
    
