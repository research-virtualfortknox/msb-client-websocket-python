# -*- coding: utf-8 -*-
"""
Copyright (c) 2019 Fraunhofer Institute for Manufacturing Engineering and Automation (IPA)
Authors: Daniel Stock, Matthias Stoehr

Licensed under the Apache License, Version 2.0
See the file "LICENSE" for the full license governing this code.
"""

from msb_client.DataType import getDataType


class DataFormat:
    """Manages the definition of simple dataformats."""

    def __init__(self, dataType=None, isArray=None):
        """Initializes a new simple dataformat.

        Args:
            dataType (:obj:DataType): The data type based on the predefined DataType list
            isArray (bool): Is the data type in an array or not.
        """
        self.isArray = isArray
        dataFormat = {}
        dataObject = {}
        if isArray:
            dataObject["type"] = "array"
            dataObject["items"] = getDataType(dataType)
            dataFormat["dataObject"] = dataObject
        else:
            dataObject = getDataType(dataType)
            dataFormat["dataObject"] = dataObject
        self.dataFormat = dataFormat

    def getDataFormat(self):
        return self.dataFormat
