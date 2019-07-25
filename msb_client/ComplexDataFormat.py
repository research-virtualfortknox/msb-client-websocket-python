# -*- coding: utf-8 -*-
"""
Copyright (c) 2019 Fraunhofer Institute for Manufacturing Engineering and Automation (IPA)
Authors: Daniel Stock, Matthias Stoehr

Licensed under the Apache License, Version 2.0
See the file "LICENSE" for the full license governing this code.
"""

from .DataType import getDataType


class ComplexDataFormat:
    """Manages the definition of self-defined (nested) complex dataformats."""

    def __init__(self, objectName):
        """Initializes a new complex dataformat.

        Args:
            objectName (str): The name of the complex dataformat.
        """
        self.objectName = objectName
        # perpare a new dataformat
        dataFormat = {}
        dataFormat[objectName] = {}
        dataFormat["dataObject"] = {}
        dataFormat[objectName]["type"] = "object"
        dataFormat["dataObject"]["$ref"] = "#/definitions/" + self.objectName
        self.dataFormat = dataFormat

    objectName = ""
    # store nested dataformats
    nested_cdf = {}

    def getDataFormat(self):
        return self.dataFormat

    def addProperty(self, propertyName, dataType, isArray=None):
        """Add a property to a complex dataformat.

        Args:
            propertyName (str): The name of the complex dataformat.
            dataType (:obj:): The datatype is an instance of :class:`ComplexDataFormat` or :class:`DataType`.
            isArray (bool): Is the dataformat in an array or not.
        """
        if isinstance(dataType, ComplexDataFormat):
            # check if datatype has to be added to the nested dataformats list
            if dataType.objectName not in list(self.nested_cdf):
                self.nested_cdf[dataType.objectName] = dataType
        # check if properties need to be initialized
        if "properties" not in self.dataFormat[self.objectName].keys():
            self.dataFormat[self.objectName]["properties"] = {}
        # add the property in the required format
        if isinstance(dataType, ComplexDataFormat):
            self.dataFormat[dataType.objectName] = {}
            dt = dataType.getDataFormat()[dataType.objectName]
            if isArray:
                if dt != {}:
                    self.dataFormat[self.objectName]["properties"][propertyName] = {}
                    self.dataFormat[self.objectName]["properties"][propertyName]["type"] = "array"
                    self.dataFormat[self.objectName]["properties"][propertyName]["items"] = {}
                    self.dataFormat[self.objectName]["properties"][propertyName]["items"][
                        "$ref"
                    ] = ("#/definitions/" + dataType.objectName)
                    self.dataFormat[dataType.objectName] = dt
            else:
                if dt != {}:
                    self.dataFormat[self.objectName]["properties"][propertyName] = {}
                    self.dataFormat[self.objectName]["properties"][propertyName][
                        "$ref"
                    ] = ("#/definitions/" + dataType.objectName)
                    self.dataFormat[dataType.objectName] = dt

        else:
            dt = getDataType(dataType)
            if isArray:
                if dt != {}:
                    self.dataFormat[self.objectName]["properties"][propertyName] = {}
                    self.dataFormat[self.objectName]["properties"][propertyName]["type"] = "array"
                    self.dataFormat[self.objectName]["properties"][propertyName]["items"] = dt
            else:
                if dt != {}:
                    self.dataFormat[self.objectName]["properties"][propertyName] = {}
                    self.dataFormat[self.objectName]["properties"][propertyName] = dt
