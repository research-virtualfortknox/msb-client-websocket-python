# -*- coding: utf-8 -*-
"""
Copyright (c) 2019 Fraunhofer Institute for Manufacturing Engineering and Automation (IPA)
Authors: Daniel Stock, Matthias Stoehr

Licensed under the Apache License, Version 2.0
See the file "LICENSE" for the full license governing this code.
"""

import copy
import json

import datetime

from .ComplexDataFormat import ComplexDataFormat
from .DataFormat import DataFormat
from .DataType import DataType, convertDataType


class Event:
    """Definition of events to be send via the MSB."""
    def __init__(
        self,
        eventId,
        event_name,
        event_description,
        event_dataFormat,
        priority=0,
        isArray=False,
    ):
        """Initializes a new event.

        Args:
            eventId (str): The event id
            event_name (str): The name of the event
            event_description (str): The description of the event
            event_dataFormat (:obj:): The data type of the event (of class DataFormat, DataType or ComplexDataFormat)
            priority (str, int): The priority of the event (LOW,MEDIUM,HIGH) or (0,1,2)
            isArray (bool): Specifies if the event handles an object array or just an object of the data
        """
        self.eventId = eventId
        self.name = event_name
        self.description = event_description
        self.priority = priority
        self.isArray = isArray
        if (
            isinstance(event_dataFormat, DataFormat) 
            or isinstance(event_dataFormat, ComplexDataFormat)
        ):
            # make a deep copy of the root dataformat
            self.dataFormat = copy.deepcopy(event_dataFormat).getDataFormat()
            # and add all nested data formats 
            for df_key in list(event_dataFormat.nested_cdf.keys()):
                if df_key not in self.dataFormat:
                    self.dataFormat[df_key] = event_dataFormat.nested_cdf[df_key].dataFormat[df_key]
            self.df = event_dataFormat
        elif isinstance(event_dataFormat, DataType):
            self.dataFormat = DataFormat(event_dataFormat, isArray).getDataFormat()
            self.df = convertDataType(event_dataFormat)
        elif type(event_dataFormat) == type(datetime):
            self.dataFormat = DataFormat(event_dataFormat, isArray).getDataFormat()
            self.df = datetime.datetime
        elif event_dataFormat is None:
            self.dataFormat = None
            self.df = None
        else:
            # also support the definition of hte dattaformat as json object
            try:
                json_object = {"dataObject": json.loads(event_dataFormat)}
                self.dataFormat = json_object
            except Exception:
                self.dataFormat = DataFormat(event_dataFormat, isArray).getDataFormat()
            self.df = event_dataFormat

    id = 0
    dataObject = 0
