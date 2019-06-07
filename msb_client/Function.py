# -*- coding: utf-8 -*-
"""
Copyright (c) 2019 Fraunhofer Institute for Manufacturing Engineering and Automation (IPA)
Authors: Daniel Stock, Matthias Stoehr

Licensed under the Apache License, Version 2.0
See the file "LICENSE" for the full license governing this code.
"""

import json
import copy

from .ComplexDataFormat import ComplexDataFormat
from .DataFormat import DataFormat
import datetime


class Function:
    """Definition of functions to be provided via the MSB."""
    def __init__(
        self,
        functionId,
        function_name,
        function_description,
        function_dataformat,
        fnpointer=None,
        isArray=False,
        responseEvents=None,
    ):
        """Initializes a new function.

        Args:
            functionId (str): The function id
            function_name (str): The name of the function
            function_description (str): The description of the function
            function_dataformat (:obj:): The data type of the function (of class DataFormat or ComplexDataFormat)
            fnpointer (:func:): The function implementation to be called for incoming events
            isArray (bool): Specifies if the function handles an object array or just an object of the data
            responseEvents (:obj: list of event ids): The list of event IDs to be send as response events
        """
        self.functionId = functionId
        self.name = function_name
        self.description = function_description
        self.implementation = fnpointer
        self.isArray = isArray
        if responseEvents is None:
            self.responseEvents = []
        else:
            self.responseEvents = responseEvents
        if (
            isinstance(function_dataformat, DataFormat) 
            or isinstance(function_dataformat, ComplexDataFormat)
        ):
            # make a deep copy of the root dataformat
            self.dataFormat = copy.deepcopy(function_dataformat).getDataFormat()
        elif type(function_dataformat) == type(datetime):
            self.dataFormat = DataFormat(function_dataformat, isArray).getDataFormat()
        elif function_dataformat is None:
            self.dataFormat = None
        else:
            # also support the definition of hte dattaformat as json object
            try:
                json_object = {"dataObject": json.loads(function_dataformat)}
                self.dataFormat = json_object
            except Exception:
                self.dataFormat = DataFormat(
                    function_dataformat, isArray
                ).getDataFormat()
