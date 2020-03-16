# -*- coding: utf-8 -*-
"""
Copyright (c) 2019 Fraunhofer Institute for Manufacturing Engineering and Automation (IPA)
Authors: Daniel Stock, Matthias Stoehr

Licensed under the Apache License, Version 2.0
See the file "LICENSE" for the full license governing this code.
"""

import datetime

from enum import Enum


class DataType(Enum):
    """Enum of all supported simple data taypes."""
    STRING = "string"
    INT32 = "int32"
    INT64 = "int64"
    DOUBLE = "double"
    FLOAT = "float"
    DATETIME = "date-time"
    BOOLEAN = "boolean"
    BYTE = "byte"


def getDataType(format):
    """Generates a valid datatype based on various format definitions.

    Args:
        format (:obj:DataType,str,bool,int,float,datetime): The format definition
    Returns:
        datatype: The datatype as valid object (compatible with json schema)
    """
    dataType = {}
    if (
        format == "string"
        or format == DataType.STRING
        or format == str
    ):
        dataType["type"] = "string"
    elif (
        format == "int32"
        or format == DataType.INT32
    ):
        dataType["type"] = "integer"
        dataType["format"] = "int32"
    elif (
        format == "int64"
        or format == DataType.INT64
        or format == int
        or format == "integer"
    ):
        dataType["type"] = "integer"
        dataType["format"] = "int64"
    elif (
        format == "float"
        or format == DataType.FLOAT
    ):
        dataType["type"] = "number"
        dataType["format"] = "float"
    elif (
        format == "double"
        or format == DataType.DOUBLE
        or format == float
        or format == "number"
    ):
        dataType["type"] = "number"
        dataType["format"] = "double"
    elif (
        format == "date-time"
        or format == DataType.DATETIME
        or format == datetime
        or format == datetime.datetime
    ):
        dataType["type"] = "string"
        dataType["format"] = "date-time"
    elif (
        format == "boolean"
        or format == DataType.BOOLEAN
        or format == bool
    ):
        dataType["type"] = "boolean"
    elif (
        format == "byte"
        or format == DataType.BYTE
    ):
        dataType["type"] = "string"
        dataType["format"] = "byte"
    else:
        raise Exception("Unknown dataType: " + str(format))
    return dataType


def convertDataType(format):
    """Converts the format to python datatype

    Args:
        format (:obj:DataType): The format definition
    Returns:
        datatype: The datatype as python datatype
    """
    dataType = {}
    if format == DataType.STRING:
        return str
    elif format == DataType.INT32:
        return int
    elif format == DataType.INT64:
        return int
    elif format == DataType.FLOAT:
        return float
    elif format == DataType.DOUBLE:
        return float
    elif format == DataType.DATETIME:
        return datetime.datetime
    elif format == DataType.BOOLEAN:
        return bool
    elif format == DataType.BYTE:
        """
        Python 2.7 with "return bytes" returns: <type 'str'>
        Python 3   with "return bytes" returns: <class 'bytes'>
        """
        return bytes
    else:
        raise Exception("Unknown dataType: " + str(format))
    return dataType
