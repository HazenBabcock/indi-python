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

def BLOBEnable(value):
    return value

def BLOBFormat(value):
    return value

def BLOBLength(value):
    return value

def BLOBValue(value):
    return value

def groupTag(value):
    return value

def labelValue(value):
    return value

def listValue(value):
    return value

def nameValue(value):
    return value

def numberFormat(value):
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

def switchRule(value):
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


#
# The INDI specification in a Pythonic form.
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
indi_spec = {

    # Commands from Device to Client.
    
    "deviceGetProperties" : {"classname" : "GetProperties",
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

    "defText" : {"base" : INDIElement,
                 "docs" : "Define one member of a text vector.",
                 "arg" : textValue,
                 "attributes" : [["name", None, True, nameValue, "Name of this text element"],
                                 ["label", None, False, labelValue, "GUI label, or use name by default"]]},

    "defNumberVector" : {"base" : INDIVector,
                         "docs" : "Define a property that holds one or more numeric values.",
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

    "defNumber" : {"base" : INDIElement,
                   "docs" : "Define one member of a number vector.",
                   "arg" : numberValue,
                   "attributes" : [["name", None, True, nameValue, "Name of this text element"],
                                   ["label", None, False, labelValue, "GUI label, or use name by default"],
                                   ["iformat", "format", True, numberFormat, "printf() style format for GUI display"],
                                   ["imin", "min", True, numberValue, "Minimal value"],
                                   ["imax", "max", True, numberValue, "Maximal value, ignore if min == max"],
                                   ["step", None, True, numberValue, "Allowed increments, ignore if 0"]]},

    "defSwitchVector" : {"base" : INDIVector,
                         "docs" : "Define a collection of switches. Rule is only a hint for use by a GUI to decide a suitable presentation style. Rules are actually implemented wholly within the Device.",
                         "arg" : listValue,
                         "attributes" : [["device", None, True, nameValue, "Name of Device"],
                                         ["name", None, True, nameValue, "Name of Property"],
                                         ["label", None, False, labelValue, "GUI label, use name by default"],
                                         ["group", None, False, groupTag, "Property group membership, blank by default"],
                                         ["state", None, True, propertyState, "Current state of Property"],
                                         ["perm", None, True, propertyPerm, "Ostensible Client controlability"],
                                         ["rule", None, True, switchRule, "Hint for GUI presentation"],
                                         ["timeout", None, False, numberValue, "Worse-case time to affect, 0 default, N/A for ro"],
                                         ["timestamp", None, False, timeValue, "Moment when these data were valid"],
                                         ["message", None, False, textValue, "Commentary"]]},

    "defSwitch" : {"base" : INDIElement,
                   "docs" : "Define one member of a text vector.",
                   "arg" : switchState,
                   "attributes" : [["name", None, True, nameValue, "Name of this text element"],
                                   ["label", None, False, labelValue, "GUI label, or use name by default"]]},

    "defLightVector" : {"base" : INDIVector,
                        "docs" : "Define a collection of passive indicator lights.",
                        "arg" : listValue,
                        "attributes" : [["device", None, True, nameValue, "Name of Device"],
                                        ["name", None, True, nameValue, "Name of Property"],
                                        ["label", None, False, labelValue, "GUI label, use name by default"],
                                        ["group", None, False, groupTag, "Property group membership, blank by default"],
                                        ["state", None, True, propertyState, "Current state of Property"],
                                        ["timestamp", None, False, timeValue, "Moment when these data were valid"],
                                        ["message", None, False, textValue, "Commentary"]]},

    "defLight" : {"base" : INDIElement,
                  "docs" : "Define one member of a light vector.",
                  "arg" : propertyState,
                  "attributes" : [["name", None, True, nameValue, "Name of this text element"],
                                  ["label", None, False, labelValue, "GUI label, or use name by default"]]},

    "defBLOBVector" : {"base" : INDIVector,
                       "docs" : "Define a property that holds one or more Binary Large Objects, BLOBs.",
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
    
    "defBLOB" : {"base" : INDIBase,
                 "docs" : "Define one member of a BLOB vector. Unlike other defXXX elements, this does not contain an initial value for the BLOB.",
                 "attributes" : [["name", None, True, nameValue, "Name of this text element"],
                                 ["label", None, False, labelValue, "GUI label, or use name by default"]]},

    "setTextVector" : {"base" : INDIVector,
                       "docs" : "Send a new set of values for a Text vector, with optional new timeout, state and message.",
                       "arg" : listValue,
                       "attributes" : [["device", None, True, nameValue, "Name of Device"],
                                       ["name", None, True, nameValue, "Name of Property"],
                                       ["state", None, False, propertyState, "State, no change if absent"],
                                       ["timeout", None, False, numberValue, "Worse-case time to affect a change"],
                                       ["timestamp", None, False, timeValue, "Moment when these data were valid"],
                                       ["message", None, False, textValue, "Commentary"]]},

    "setNumberVector" : {"base" : INDIVector,
                         "docs" : "Send a new set of values for a Number vector, with optional new timeout, state and message.",
                         "arg" : listValue,
                         "attributes" : [["device", None, True, nameValue, "Name of Device"],
                                         ["name", None, True, nameValue, "Name of Property"],
                                         ["state", None, False, propertyState, "State, no change if absent"],
                                         ["timeout", None, False, numberValue, "Worse-case time to affect a change"],
                                         ["timestamp", None, False, timeValue, "Moment when these data were valid"],
                                         ["message", None, False, textValue, "Commentary"]]},

    "setSwitchVector" : {"base" : INDIVector,
                         "docs" : "Send a new set of values for a Switch vector, with optional new timeout, state and message.",
                         "arg" : listValue,
                         "attributes" : [["device", None, True, nameValue, "Name of Device"],
                                         ["name", None, True, nameValue, "Name of Property"],
                                         ["state", None, False, propertyState, "State, no change if absent"],
                                         ["timeout", None, False, numberValue, "Worse-case time to affect a change"],
                                         ["timestamp", None, False, timeValue, "Moment when these data were valid"],
                                         ["message", None, False, textValue, "Commentary"]]},

    "setLightVector" : {"base" : INDIVector,
                        "docs" : "Send a new set of values for a Light vector, with optional new state and message.",
                        "arg" : listValue,
                        "attributes" : [["device", None, True, nameValue, "Name of Device"],
                                        ["name", None, True, nameValue, "Name of Property"],
                                        ["state", None, False, propertyState, "State, no change if absent"],
                                        ["timestamp", None, False, timeValue, "Moment when these data were valid"],
                                        ["message", None, False, textValue, "Commentary"]]},

    "setBLOBVector" : {"base" : INDIVector,
                       "docs" : "Send a new set of values for a BLOB vector, with optional new timeout, state and message.",
                       "arg" : listValue,
                       "attributes" : [["device", None, True, nameValue, "Name of Device"],
                                       ["name", None, True, nameValue, "Name of Property"],
                                       ["state", None, False, propertyState, "State, no change if absent"],
                                       ["timeout", None, False, numberValue, "Worse-case time to affect a change"],
                                       ["timestamp", None, False, timeValue, "Moment when these data were valid"],
                                       ["message", None, False, textValue, "Commentary"]]},

    "message" : {"base" : INDIBase,
                 "docs" : "Send a message associated with a device or entire system.",
                 "attributes" : [["device", None, True, nameValue, "Considered to be site-wide if absent"],
                                 ["timestamp", None, False, timeValue, "Moment when this message was generated"],
                                 ["message", None, False, textValue, "Commentary"]]},

    "delProperty" : {"base" : INDIBase,
                     "docs" : "Delete the given property, or entire device if no property is specified.",
                     "attributes" : [["device", None, True, nameValue, "Name of Device"],
                                     ["name", None, False, nameValue, "Entire device if absent"],
                                     ["timestamp", None, False, timeValue, "Moment when this delete was generated"],
                                     ["message", None, False, textValue, "Commentary"]]},

    "oneLight" : {"base" : INDIElement,
                  "docs" : "Send a message to specify state of one member of a Light vector.",
                  "arg" : propertyState,
                  "attributes" : [["name", None, True, nameValue, "Name of this light element"]]},

    
    # Commands from Client to Device.

    "clientGetProperties" : {"classname" : "GetProperties",
                             "xml" : "getProperties",
                             "base" : INDIBase,
                             "docs" : "Command to ask Device to define all Properties, or those for a specific Device or specific Property, for which it is responsible. Must always include protocol version.",
                             "attributes" : [["version", None, True, nameValue, "protocol version"],
                                             ["device", None, False, nameValue, "device to snoop, or all if absent"],
                                             ["name", None, False, nameValue, "property of device to snoop, or all if absent"]]},

    "enableBLOB" : {"base" : INDIElement,
                    "docs" : "Command to control whether setBLOBs should be sent to this channel from a given Device. They can be turned off completely by setting Never (the default), allowed to be intermixed with other INDI commands by setting Also or made the only command by setting Only.",
                    "arg" : BLOBEnable,
                    "attributes" : [["device", None, False, labelValue, "Name of Device"],
                                    ["name", None, False, labelValue, "Name of BLOB Property, or all if absent"]]},

    "newTextVector" : {"base" : INDIVector,
                       "docs" : "Send new target text values.",
                       "arg" : listValue,
                       "attributes" : [["device", None, True, nameValue, "Name of Device"],
                                       ["name", None, True, nameValue, "Name of Property"],
                                       ["timestamp", None, False, timeValue, "Moment when this message was generated"]]},

    "newNumberVector" : {"base" : INDIVector,
                         "docs" : "Send new target numeric values.",
                         "arg" : listValue,
                         "attributes" : [["device", None, True, nameValue, "Name of Device"],
                                         ["name", None, True, nameValue, "Name of Property"],
                                         ["timestamp", None, False, timeValue, "Moment when this message was generated"]]},

    "newSwitchVector" : {"base" : INDIVector,
                         "docs" : "Send new target switch states.",
                         "arg" : listValue,
                         "attributes" : [["device", None, True, nameValue, "Name of Device"],
                                         ["name", None, True, nameValue, "Name of Property"],
                                         ["timestamp", None, False, timeValue, "Moment when this message was generated"]]},

    "newBLOBVector" : {"base" : INDIVector,
                       "docs" : "Send new target BLOBS.",
                       "arg" : listValue,
                       "attributes" : [["device", None, True, nameValue, "Name of Device"],
                                       ["name", None, True, nameValue, "Name of Property"],
                                       ["timestamp", None, False, timeValue, "Moment when this message was generated"]]},
    

    # Elements describing a vector member value, used in both directions.

    "oneText" : {"base" : INDIElement,
                 "docs" : "One member of a text vector.",
                 "arg" : textValue,
                 "attributes" : [["name", None, True, nameValue, "Name of this text element"]]},

    "oneNumber" : {"base" : INDIElement,
                   "docs" : "One member of a number vector.",
                   "arg" : numberValue,
                   "attributes" : [["name", None, True, nameValue, "Name of this number element"]]},

    "oneSwitch" : {"base" : INDIElement,
                   "docs" : "One member of a switch vector.",
                   "arg" : switchState,
                   "attributes" : [["name", None, True, nameValue, "Name of this switch element"]]},

    "oneBLOB" : {"base" : INDIElement,
                 "docs" : "One member of a BLOB vector. The contents of this element must always be encoded using base64. The format attribute consists of one or more file name suffixes, each preceded with a period, which indicate how the decoded data is to be interpreted. For example .fits indicates the decoded BLOB is a FITS file, and .fits.z indicates the decoded BLOB is a FITS file compressed with zlib. The INDI protocol places no restrictions on the contents or formats of BLOBs but at minimum astronomical INDI clients are encouraged to support the FITS image file format and the zlib compression mechanism. The size attribute indicates the number of bytes in the final BLOB after decoding and after any decompression. For example, if the format is .fits.z the size attribute is the number of bytes in the FITS file. A Client unfamiliar with the specified format may use the attribute as a simple string, perhaps in combination with the timestamp attribute, to create a file name in which to store the data without processing other than decoding the base64.",
                 "arg" : BLOBValue,
                 "attributes" : [["name", None, True, nameValue, "Name of this BLOB element"],
                                 ["size", None, True, BLOBLength, "Number of bytes in decoded and uncompressed BLOB"],
                                 ["iformat", "format", True, BLOBFormat, "Format as a file suffix, eg: .z, .fits, .fits.z"]]},    

}


def makeINDIFn(indi_type):
    """
    Returns an INDI function of the requested type.
    """
    global indi_spec
    
    # Check that the requested type exists.
    if not indi_type in indi_spec:
        raise IndiXMLException(indi_type + " is not a valid INDI XML command type.")

    type_spec = indi_spec[indi_type]

    # Function to make the object.
    def makeObject(fn_arg, fn_attr):

        # Check attributes against those in the specification.
        all_attr = []
        final_attr = {}
        for attr in type_spec["attributes"]:
            attr_name = attr[0]
            all_attr.append(attr_name)

            # Check if required.
            if attr[2] and not attr_name in fn_attr:
                raise IndiXMLException(attr_name + " is a required attribute.")

            # Check if valid.
            if attr_name in fn_attr:
                if attr[1] is None:
                    attr[1] = attr[0]
                final_attr[attr[1]] = attr[3](fn_attr[attr_name])

        # Check that there are no extra attributes.
        for attr in fn_attr:
            if not attr in all_attr:
                raise IndiXMLException(attr + " is not an attribute of " + indi_type + ".")

        # Check if we already have a class with the right name.
        if not hasattr(type_spec, "indi_class"):

            # Use (capitalized) XML command name
            if not hasattr(type_spec, "class"):
                type_spec["classname"] = indi_type[0].upper() + indi_type[1:]
            
            type_spec["class"] = type(type_spec["classname"], (type_spec["base"],), {})

        # Make an INDI object of this class.
        return type_spec["class"](type_spec["classname"], fn_arg, final_attr, None)

    # Check if an argument was expected.
    if hasattr(type_spec, "arg"):

        def ifunction(arg, indi_attr = None):
            
            # Check argument with validator function.
            arg = type_spec["arg"](arg)

            # Create object.
            return makeObject(arg, indi_attr)

    else:
        
        def ifunction(indi_attr = None):

            # Create object.
            return makeObject(None, indi_attr)

    # Manipulate some properties of the function so that help, etc. is clearer.
    ifunction.__name__ = indi_type
    ifunction.__doc__ = type_spec["docs"]  # FIXME: Add arguments dictionary.
    
    return ifunction


#
# The API
#

def fromINDIXML(xml):
    pass

deviceGetProperties = makeINDIFn("deviceGetProperties")
defTextVector = makeINDIFn("defTextVector")
defText = makeINDIFn("defText")
defNumberVector = makeINDIFn("defNumberVector")
defNumber = makeINDIFn("defNumber")
defSwitchVector = makeINDIFn("defSwitchVector")
defSwitch = makeINDIFn("defSwitch")
defLightVector = makeINDIFn("defLightVector")
defLight = makeINDIFn("defLight")
defBLOBVector = makeINDIFn("defBLOBVector")
defBLOB = makeINDIFn("defBLOB")
setTextVector = makeINDIFn("setTextVector")
setNumberVector = makeINDIFn("setNumberVector")
setSwitchVector = makeINDIFn("setSwitchVector")
setLightVector = makeINDIFn("setLightVector")
setBLOBVector = makeINDIFn("setBLOBVector")
message = makeINDIFn("message")
delProperty = makeINDIFn("delProperty")
oneLight = makeINDIFn("oneLight")

clientGetProperties = makeINDIFn("clientGetProperties")
enableBLOB = makeINDIFn("enableBLOB")
newTextVector = makeINDIFn("newTextVector")
newNumberVector = makeINDIFn("newNumberVector")
newSwitchVector = makeINDIFn("newSwitchVector")
newBLOBVector = makeINDIFn("newBLOBVector")

oneText = makeINDIFn("oneText")
oneNumber = makeINDIFn("oneNumber")
oneSwitch = makeINDIFn("oneSwitch")
oneBLOB = makeINDIFn("oneBLOB")


#
# Simple tests.
#
if (__name__ == "__main__"):
    gp = clientGetProperties(indi_attr = {"version" : "1.0", "name" : "bar"})
    print(gp)
    print(ElementTree.tostring(gp.toXML(), 'utf-8'))

    gp.setAttr("name", "baz")
    print(ElementTree.tostring(gp.toXML(), 'utf-8'))

    print(gp.getValue())

    
    
