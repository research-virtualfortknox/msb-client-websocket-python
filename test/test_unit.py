"""
MSBClientIntegrationTest is an integration test for the MSB Python client library.
Copyright (c) 2017
Fraunhofer Institute for Manufacturing Engineering and Automation (IPA)
Author: Daniel Stock
mailto: daniel DOT stock AT ipa DOT fraunhofer DOT com
See the file "LICENSE" for the full license governing this code.
"""
import datetime

import pytest
import logging
import uuid
import json

import sys

from msb_client.ComplexDataFormat import ComplexDataFormat
from msb_client.DataType import DataType
from msb_client.Event import Event
from msb_client.Function import Function
from msb_client.MsbClient import MsbClient

try:
    import unittest2 as unittest
except ImportError:
    import unittest

FORMAT = "%(asctime)s %(levelname)s %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)

# Main constants
OWNER_UUID = str(uuid.uuid4())
SERVICE_TYPE = "SmartObject"
SO_UUID = str(uuid.uuid4())
SO_NAME = "MSBClientUnitTestSO" + SO_UUID[-6:]
SO_DESCRIPTION = "MSBClientUnitTestSO description"
SO_TOKEN = SO_UUID[-6:]
FLOW_NAME = str(uuid.uuid4())
CORRELATIOON_ID_FOR_TEST = str(uuid.uuid4())


class TestMSBClientBasicInitialization(unittest.TestCase):
    """
    Test basic client initializazion and client settings functions
    """

    def test_getClientParametersFromApplicationPropertiesFile(self):
        # 1. ARRANGE
        # 2. ACT
        myMsbClient = MsbClient()
        # 3. ASSERT
        self.assertIsNotNone(myMsbClient.service_type)
        self.assertIsNotNone(myMsbClient.uuid)
        self.assertIsNotNone(myMsbClient.name)
        self.assertIsNotNone(myMsbClient.description)
        self.assertIsNotNone(myMsbClient.token)

    def test_getClientParametersFromApplicationPropertiesFileWithCustomPath(self):
        # 1. ARRANGE
        # 2. ACT
        myMsbClient = MsbClient(applicationPropertiesCustomPath="./test/application-test.properties")
        # 3. ASSERT
        self.assertIsNotNone(myMsbClient.service_type)
        self.assertIsNotNone(myMsbClient.uuid)
        self.assertIsNotNone(myMsbClient.name)
        self.assertEqual(myMsbClient.name, "PythonTest Custom Path")
        self.assertIsNotNone(myMsbClient.description)
        self.assertIsNotNone(myMsbClient.token)

    def test_getClientParametersIfSetViaConstructor(self):
        # 1. ARRANGE
        # 2. ACT
        myMsbClient = MsbClient(
            SERVICE_TYPE,
            SO_UUID,
            SO_NAME,
            SO_DESCRIPTION,
            SO_TOKEN
        )
        # 3. ASSERT
        self.assertEqual(myMsbClient.service_type, SERVICE_TYPE)
        self.assertEqual(myMsbClient.uuid, SO_UUID)
        self.assertEqual(myMsbClient.name, SO_NAME)
        self.assertEqual(myMsbClient.description, SO_DESCRIPTION)
        self.assertEqual(myMsbClient.token, SO_TOKEN)

    def test_updateInitialClientSettingsByFunctions(self):
        # 1. ARRANGE
        # choose settings that change the default values, to check if they get updated as expected
        debug = True
        dataFormatValidation = False
        disableEventCache = True
        eventCacheSize = 500
        disableAutoReconnect = True
        # min value is 3000
        reconnectIntervalMinimum = 3000
        reconnectInterval = 2000
        disableHostNameVerification = True
        disableSockJsFraming = True
        keepAlive = True
        heartbeatIntervalMinimum = 8000
        heartbeatInterval = 5000
        threadAsDaemon = True

        myMsbClient = MsbClient()
        # 2. ACT
        myMsbClient.enableDebug(not debug)
        myMsbClient.enableDebug(debug)
        myMsbClient.enableDataFormatValidation(dataFormatValidation)
        myMsbClient.disableEventCache(disableEventCache)
        myMsbClient.setEventCacheSize(eventCacheSize)
        myMsbClient.disableAutoReconnect(disableAutoReconnect)
        myMsbClient.setReconnectInterval(reconnectInterval)
        myMsbClient.disableHostnameVerification(disableHostNameVerification)
        myMsbClient.disableSockJsFraming(disableSockJsFraming)
        myMsbClient.setKeepAlive(keepAlive, heartbeatInterval)
        myMsbClient.enableThreadAsDaemon(threadAsDaemon)

        # 3. ASSERT
        self.assertEqual(myMsbClient.debug, debug)
        self.assertEqual(myMsbClient.dataFormatValidation, dataFormatValidation)
        self.assertEqual(myMsbClient.eventCacheEnabled, not disableEventCache)
        self.assertEqual(myMsbClient.eventCacheSize, eventCacheSize)
        self.assertEqual(myMsbClient.autoReconnect, not disableAutoReconnect)
        self.assertEqual(myMsbClient.reconnectInterval, reconnectIntervalMinimum / 1000)
        self.assertEqual(myMsbClient.hostnameVerification, not disableHostNameVerification)
        self.assertEqual(myMsbClient.sockJsFraming, not disableSockJsFraming)
        self.assertEqual(myMsbClient.keepAlive, keepAlive)
        self.assertEqual(myMsbClient.heartbeat_interval, heartbeatIntervalMinimum / 1000)
        self.assertEqual(myMsbClient.threadAsDaemonEnabled, threadAsDaemon)


class TestMSBClientConfigurationParameters(unittest.TestCase):
    """
    Test management of configutation parameters for the client
    """

    def test_addClientConfigurationParameters(self):
        # 1. ARRANGE
        param_name_1 = "testParam1"
        param_value_1 = True
        param_datatype_1 = bool

        param_name_2 = "testParam2"
        param_value_2 = "StringValue"
        param_datatype_2 = str

        param_name_3 = "testParam3"
        param_value_3 = 1000
        param_datatype_3 = "int32"

        param_name_4 = "testParam3_2"
        param_value_4 = 2000
        param_datatype_4 = int

        param_name_5 = "testParam5"
        param_value_5 = 3.3
        param_datatype_5 = float

        param_name_6 = "testParam6"
        param_value_6 = 3.3
        param_datatype_6 = "float"

        param_name_7 = "testParam7"
        param_value_7 = datetime.datetime.now()
        param_datatype_7 = "date-time"

        param_name_8 = "testParam8"
        param_value_8 = b"Bytes objects are immutable sequences of single bytes"
        param_datatype_8 = "byte"

        param_name_9 = "testParam9"
        param_value_9 = 12
        param_datatype_9 = "Invalid"
        errorOnInvalidDatatype = False

        # 2. ACT
        myMsbClient = MsbClient()
        myMsbClient.addConfigParameter(param_name_1, param_value_1, param_datatype_1)
        myMsbClient.addConfigParameter(param_name_2, param_value_2, param_datatype_2)
        myMsbClient.addConfigParameter(param_name_3, param_value_3, param_datatype_3)
        myMsbClient.addConfigParameter(param_name_4, param_value_4, param_datatype_4)
        myMsbClient.addConfigParameter(param_name_5, param_value_5, param_datatype_5)
        myMsbClient.addConfigParameter(param_name_6, param_value_6, param_datatype_6)
        myMsbClient.addConfigParameter(param_name_7, param_value_7, param_datatype_7)
        myMsbClient.addConfigParameter(param_name_8, param_value_8, param_datatype_8)
        try:
            myMsbClient.addConfigParameter(param_name_9, param_value_9, param_datatype_9)
        except Exception:
            errorOnInvalidDatatype = True

        # 3. ASSERT
        self.assertEqual(myMsbClient.configuration["parameters"][param_name_1]["value"], param_value_1)
        self.assertEqual(myMsbClient.configuration["parameters"][param_name_1]["type"], "BOOLEAN")
        self.assertEqual(myMsbClient.configuration["parameters"][param_name_2]["value"], param_value_2)
        self.assertEqual(myMsbClient.configuration["parameters"][param_name_2]["type"], "STRING")
        self.assertEqual(myMsbClient.configuration["parameters"][param_name_3]["value"], param_value_3)
        self.assertEqual(myMsbClient.configuration["parameters"][param_name_3]["type"], "INTEGER")
        self.assertEqual(myMsbClient.configuration["parameters"][param_name_3]["format"], "INT32")
        self.assertEqual(myMsbClient.configuration["parameters"][param_name_4]["value"], param_value_4)
        self.assertEqual(myMsbClient.configuration["parameters"][param_name_4]["type"], "INTEGER")
        self.assertEqual(myMsbClient.configuration["parameters"][param_name_4]["format"], "INT64")
        self.assertEqual(myMsbClient.configuration["parameters"][param_name_5]["value"], param_value_5)
        self.assertEqual(myMsbClient.configuration["parameters"][param_name_5]["type"], "NUMBER")
        self.assertEqual(myMsbClient.configuration["parameters"][param_name_5]["format"], "DOUBLE")
        self.assertEqual(myMsbClient.configuration["parameters"][param_name_6]["value"], param_value_6)
        self.assertEqual(myMsbClient.configuration["parameters"][param_name_6]["type"], "NUMBER")
        self.assertEqual(myMsbClient.configuration["parameters"][param_name_6]["format"], "FLOAT")
        self.assertEqual(myMsbClient.configuration["parameters"][param_name_7]["value"], str(param_value_7))
        self.assertEqual(myMsbClient.configuration["parameters"][param_name_7]["type"], "STRING")
        self.assertEqual(myMsbClient.configuration["parameters"][param_name_7]["format"], "DATE-TIME")
        self.assertEqual(myMsbClient.configuration["parameters"][param_name_8]["value"], param_value_8)
        self.assertEqual(myMsbClient.configuration["parameters"][param_name_8]["type"], "STRING")
        self.assertEqual(myMsbClient.configuration["parameters"][param_name_8]["format"], "BYTE")
        self.assertEqual(errorOnInvalidDatatype, True)

    def test_getValueOfClientConfigurationParameters(self):
        # 1. ARRANGE
        param_name_1 = "testParam1"
        param_value_1 = True
        param_datatype_1 = bool

        param_name_2 = "testParam2"
        param_value_2 = "StringValue"
        param_datatype_2 = str

        param_name_3 = "testParam3"
        param_value_3 = 1000
        param_datatype_3 = "int32"

        param_name_4 = "testParam3_2"
        param_value_4 = 2000
        param_datatype_4 = int

        errorOnInvalidKey = False

        # 2. ACT
        myMsbClient = MsbClient()
        myMsbClient.addConfigParameter(param_name_1, param_value_1, param_datatype_1)
        myMsbClient.addConfigParameter(param_name_2, param_value_2, param_datatype_2)
        myMsbClient.addConfigParameter(param_name_3, param_value_3, param_datatype_3)
        myMsbClient.addConfigParameter(param_name_4, param_value_4, param_datatype_4)

        # 3. ASSERT
        self.assertEqual(myMsbClient.getConfigParameter(param_name_1), param_value_1)
        self.assertEqual(myMsbClient.getConfigParameter(param_name_2), param_value_2)
        self.assertEqual(myMsbClient.getConfigParameter(param_name_3), param_value_3)
        self.assertEqual(myMsbClient.getConfigParameter(param_name_4), param_value_4)
        try:
            myMsbClient.getConfigParameter("InvalidKey")
        except Exception:
            errorOnInvalidKey = True
        self.assertEqual(errorOnInvalidKey, True)

    def test_changeClientConfigurationParameters(self):
        # 1. ARRANGE
        param_name_1 = "testParam1"
        param_value_1 = True
        param_new_value_1 = False
        param_datatype_1 = bool

        param_name_2 = "testParam2"
        param_value_2 = "StringValue"
        param_new_value_2 = "StringValue"
        param_datatype_2 = str

        param_name_3 = "testParam3"
        param_value_3 = 1000
        param_new_value_3 = 50
        param_datatype_3 = "int32"

        # 2. ACT
        myMsbClient = MsbClient()
        myMsbClient.addConfigParameter(param_name_1, param_value_1, param_datatype_1)
        myMsbClient.addConfigParameter(param_name_2, param_value_2, param_datatype_2)
        myMsbClient.addConfigParameter(param_name_3, param_value_3, param_datatype_3)
        # change
        myMsbClient.changeConfigParameter(param_name_1, param_new_value_1)
        # do not change (same value)
        myMsbClient.changeConfigParameter(param_name_2, param_new_value_2)
        # do not change (invalid key)
        myMsbClient.changeConfigParameter("testParam3_hmmm", param_new_value_3)

        # 3. ASSERT
        self.assertEqual(myMsbClient.getConfigParameter(param_name_1), param_new_value_1)
        self.assertEqual(myMsbClient.getConfigParameter(param_name_2), param_value_2)
        self.assertEqual(myMsbClient.getConfigParameter(param_name_3), param_value_3)


class TestMSBClientCreateClientFunctions(unittest.TestCase):
    """
    Test the creation of client functions
    """

    def test_addClientFunctionPerSingleParam(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        function_id = str(uuid.uuid4())[-6:]
        function_name = "FUNC " + function_id
        function_description = "FUNC Description " + function_id
        function_dataformat = "string"
        isArray = False
        responseEvents = None

        # 2. ACT
        myMsbClient.addFunction(
            function_id,
            function_name,
            function_description,
            function_dataformat,
            printMsg,
            isArray,
            responseEvents,
        )

        # 3. ASSERT
        self.assertEqual(myMsbClient.functions[function_id].functionId, function_id)
        self.assertEqual(myMsbClient.functions[function_id].name, function_name)
        self.assertEqual(myMsbClient.functions[function_id].description, function_description)
        self.assertEqual(myMsbClient.functions[function_id].isArray, isArray)
        self.assertEqual(myMsbClient.functions[function_id].dataFormat["dataObject"]["type"], function_dataformat)
        self.assertEqual(len(myMsbClient.functions[function_id].responseEvents), 0)
        self.assertEqual(myMsbClient.functions[function_id].implementation, printMsg)

    def test_addClientFunctionPerFunctionObject(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        function_id = str(uuid.uuid4())[-6:]
        function_name = "FUNC " + function_id
        function_description = "FUNC Description " + function_id
        function_dataformat = "string"
        isArray = False
        responseEvents = []

        # 2. ACT
        function = Function(
            function_id,
            function_name,
            function_description,
            function_dataformat,
            printMsg,
            isArray,
            responseEvents,
        )
        myMsbClient.addFunction(function)

        # 3. ASSERT
        self.assertEqual(myMsbClient.functions[function_id].functionId, function_id)
        self.assertEqual(myMsbClient.functions[function_id].name, function_name)
        self.assertEqual(myMsbClient.functions[function_id].description, function_description)
        self.assertEqual(myMsbClient.functions[function_id].isArray, isArray)
        self.assertEqual(myMsbClient.functions[function_id].dataFormat["dataObject"]["type"], function_dataformat)
        self.assertEqual(len(myMsbClient.functions[function_id].responseEvents), len(responseEvents))
        self.assertEqual(myMsbClient.functions[function_id].implementation, printMsg)

    def test_addClientFunctionPerSingleParamNonStaticFunctionPointer(self):
        # 1. ARRANGE
        myInstance = myClass()
        myMsbClient = MsbClient()

        function_id = str(uuid.uuid4())[-6:]
        function_name = "FUNC " + function_id
        function_description = "FUNC Description " + function_id
        function_dataformat = "string"
        isArray = False
        responseEvents = None

        # 2. ACT
        myMsbClient.addFunction(
            function_id,
            function_name,
            function_description,
            function_dataformat,
            myInstance.myNonStaticPrintMethod,
            isArray,
            responseEvents,
        )

        # 3. ASSERT
        print("NON STATIC METHOD: " + str(myMsbClient.getSelfDescription()))
        self.assertEqual(myMsbClient.functions[function_id].functionId, function_id)
        self.assertEqual(myMsbClient.functions[function_id].name, function_name)
        self.assertEqual(myMsbClient.functions[function_id].description, function_description)
        self.assertEqual(myMsbClient.functions[function_id].isArray, isArray)
        self.assertEqual(myMsbClient.functions[function_id].dataFormat["dataObject"]["type"], function_dataformat)
        self.assertEqual(len(myMsbClient.functions[function_id].responseEvents), 0)
        self.assertEqual(myMsbClient.functions[function_id].implementation, myInstance.myNonStaticPrintMethod)

    def test_addClientFunctionPerSingleParamWithJsonString(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        function_id = str(uuid.uuid4())[-6:]
        function_name = "FUNC " + function_id
        function_description = "FUNC Description " + function_id
        function_dataformat = '{ "type": "number",  "format": "float" }'
        isArray = False
        responseEvents = None

        # 2. ACT
        myMsbClient.addFunction(
            function_id,
            function_name,
            function_description,
            function_dataformat,
            printMsg,
            isArray,
            responseEvents,
        )

        # 3. ASSERT
        self.assertEqual(myMsbClient.functions[function_id].functionId, function_id)
        self.assertEqual(myMsbClient.functions[function_id].name, function_name)
        self.assertEqual(myMsbClient.functions[function_id].description, function_description)
        self.assertEqual(myMsbClient.functions[function_id].isArray, isArray)
        self.assertEqual(myMsbClient.functions[function_id].dataFormat["dataObject"]["type"], "number")
        self.assertEqual(myMsbClient.functions[function_id].dataFormat["dataObject"]["format"], "float")
        self.assertEqual(len(myMsbClient.functions[function_id].responseEvents), 0)
        self.assertEqual(myMsbClient.functions[function_id].implementation, printMsg)

    def test_addClientFunctionPerSingleParamWithArray(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        function_id = str(uuid.uuid4())[-6:]
        function_name = "FUNC " + function_id
        function_description = "FUNC Description " + function_id
        function_dataformat = "string"
        isArray = True
        responseEvents = []

        # 2. ACT
        myMsbClient.addFunction(
            function_id,
            function_name,
            function_description,
            function_dataformat,
            printMsg,
            isArray,
            responseEvents,
        )

        # 3. ASSERT
        self.assertEqual(myMsbClient.functions[function_id].functionId, function_id)
        self.assertEqual(myMsbClient.functions[function_id].name, function_name)
        self.assertEqual(myMsbClient.functions[function_id].description, function_description)
        self.assertEqual(myMsbClient.functions[function_id].isArray, isArray)
        self.assertEqual(myMsbClient.functions[function_id].dataFormat["dataObject"]["type"], "array")
        self.assertEqual(myMsbClient.functions[function_id].dataFormat["dataObject"]
                         ["items"]["type"], function_dataformat)
        self.assertEqual(len(myMsbClient.functions[function_id].responseEvents), len(responseEvents))
        self.assertEqual(myMsbClient.functions[function_id].implementation, printMsg)

    def test_addClientFunctionPerFunctionObjectWithArray(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        function_id = str(uuid.uuid4())[-6:]
        function_name = "FUNC " + function_id
        function_description = "FUNC Description " + function_id
        function_dataformat = "string"
        isArray = True
        responseEvents = []

        # 2. ACT
        function = Function(
            function_id,
            function_name,
            function_description,
            function_dataformat,
            printMsg,
            isArray,
            responseEvents,
        )
        myMsbClient.addFunction(function)

        # 3. ASSERT
        self.assertEqual(myMsbClient.functions[function_id].functionId, function_id)
        self.assertEqual(myMsbClient.functions[function_id].name, function_name)
        self.assertEqual(myMsbClient.functions[function_id].description, function_description)
        self.assertEqual(myMsbClient.functions[function_id].isArray, isArray)
        self.assertEqual(myMsbClient.functions[function_id].dataFormat["dataObject"]["type"], "array")
        self.assertEqual(myMsbClient.functions[function_id].dataFormat["dataObject"]
                         ["items"]["type"], function_dataformat)
        self.assertEqual(len(myMsbClient.functions[function_id].responseEvents), len(responseEvents))
        self.assertEqual(myMsbClient.functions[function_id].implementation, printMsg)

    def test_addClientFunctionPerSingleParamWithNoPayload(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        function_id = str(uuid.uuid4())[-6:]
        function_name = "FUNC " + function_id
        function_description = "FUNC Description " + function_id
        function_dataformat = None
        isArray = False
        responseEvents = []

        # 2. ACT
        myMsbClient.addFunction(
            function_id,
            function_name,
            function_description,
            function_dataformat,
            printMsg,
            isArray,
            responseEvents,
        )

        # 3. ASSERT
        self.assertEqual(myMsbClient.functions[function_id].functionId, function_id)
        self.assertEqual(myMsbClient.functions[function_id].name, function_name)
        self.assertEqual(myMsbClient.functions[function_id].description, function_description)
        self.assertEqual(myMsbClient.functions[function_id].isArray, isArray)
        self.assertIsNone(myMsbClient.functions[function_id].dataFormat)
        self.assertEqual(len(myMsbClient.functions[function_id].responseEvents), len(responseEvents))
        self.assertEqual(myMsbClient.functions[function_id].implementation, printMsg)

    def test_addClientFunctionPerFunctionObjectWithNoPayload(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        function_id = str(uuid.uuid4())[-6:]
        function_name = "FUNC " + function_id
        function_description = "FUNC Description " + function_id
        function_dataformat = None
        isArray = False
        responseEvents = []

        # 2. ACT
        function = Function(
            function_id,
            function_name,
            function_description,
            function_dataformat,
            printMsg,
            isArray,
            responseEvents,
        )
        myMsbClient.addFunction(function)

        # 3. ASSERT
        self.assertEqual(myMsbClient.functions[function_id].functionId, function_id)
        self.assertEqual(myMsbClient.functions[function_id].name, function_name)
        self.assertEqual(myMsbClient.functions[function_id].description, function_description)
        self.assertEqual(myMsbClient.functions[function_id].isArray, isArray)
        self.assertIsNone(myMsbClient.functions[function_id].dataFormat)
        self.assertEqual(len(myMsbClient.functions[function_id].responseEvents), len(responseEvents))
        self.assertEqual(myMsbClient.functions[function_id].implementation, printMsg)

    def test_addClientFunctionPerSingleParamWithResponseEvents(self):
        # TODO: Add events first / implement check if events are present in  myMsbClient.events
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_1_id = str(uuid.uuid4())[-6:]
        event_1_name = "EVENT " + event_1_id
        event_1_description = "EVENT Description " + event_1_id
        event_1_dataformat = int
        event_1_priority = 2
        event_1_isArray = False

        event_2_id = str(uuid.uuid4())[-6:]
        event_2_name = "EVENT " + event_2_id
        event_2_description = "EVENT Description " + event_2_id
        event_2_dataformat = float
        event_2_priority = 1
        event_2_isArray = True

        function_id = str(uuid.uuid4())[-6:]
        function_name = "FUNC " + function_id
        function_description = "FUNC Description " + function_id
        function_dataformat = None
        isArray = False
        responseEvents = [event_1_id, event_2_id]

        # 2. ACT
        myMsbClient.addEvent(
            event_1_id,
            event_1_name,
            event_1_description,
            event_1_dataformat,
            event_1_priority,
            event_1_isArray
        )
        myMsbClient.addEvent(
            event_2_id,
            event_2_name,
            event_2_description,
            event_2_dataformat,
            event_2_priority,
            event_2_isArray
        )
        myMsbClient.addFunction(
            function_id,
            function_name,
            function_description,
            function_dataformat,
            printMsg,
            isArray,
            responseEvents,
        )

        # 3. ASSERT
        self.assertEqual(myMsbClient.functions[function_id].functionId, function_id)
        self.assertEqual(myMsbClient.functions[function_id].name, function_name)
        self.assertEqual(myMsbClient.functions[function_id].description, function_description)
        self.assertEqual(myMsbClient.functions[function_id].isArray, isArray)
        self.assertIsNone(myMsbClient.functions[function_id].dataFormat)
        self.assertEqual(myMsbClient.functions[function_id].responseEvents[0], event_1_id)
        self.assertEqual(myMsbClient.functions[function_id].responseEvents[1], event_2_id)
        self.assertEqual(myMsbClient.functions[function_id].implementation, printMsg)

    def test_doNotAddClientFunctionPerSingleParamWithInvalidResponseEvents(self):
        # TODO: Add events first / implement check if events are present in  myMsbClient.events
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_1_id = str(uuid.uuid4())[-6:]
        event_1_name = "EVENT " + event_1_id
        event_1_description = "EVENT Description " + event_1_id
        event_1_dataformat = int
        event_1_priority = 2
        event_1_isArray = False

        event_2_id = str(uuid.uuid4())[-6:]
        event_2_name = "EVENT " + event_2_id
        event_2_description = "EVENT Description " + event_2_id
        event_2_dataformat = float
        event_2_priority = 1
        event_2_isArray = True

        function_id = str(uuid.uuid4())[-6:]
        function_name = "FUNC " + function_id
        function_description = "FUNC Description " + function_id
        function_dataformat = None
        isArray = False
        responseEvents = [event_1_id, "InvalidE2"]

        # 2. ACT
        myMsbClient.addEvent(
            event_1_id,
            event_1_name,
            event_1_description,
            event_1_dataformat,
            event_1_priority,
            event_1_isArray
        )
        myMsbClient.addEvent(
            event_2_id,
            event_2_name,
            event_2_description,
            event_2_dataformat,
            event_2_priority,
            event_2_isArray
        )
        errorOnInvalidEvent = False
        try:
            myMsbClient.addFunction(
                function_id,
                function_name,
                function_description,
                function_dataformat,
                printMsg,
                isArray,
                responseEvents,
            )
        except Exception as error:
            logging.error(repr(error))
            errorOnInvalidEvent = True

        # 3. ASSERT
        self.assertEqual(errorOnInvalidEvent, True)

    def test_doNotAddDuplicateClientFunctionPerSingleParam(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        function_id = str(uuid.uuid4())[-6:]
        function_name = "FUNC " + function_id
        function_description = "FUNC Description " + function_id
        function_dataformat = "string"
        isArray = False
        responseEvents = []

        # 2. ACT
        myMsbClient.addFunction(
            function_id,
            function_name,
            function_description,
            function_dataformat,
            printMsg,
            isArray,
            responseEvents,
        )
        same_function_id = function_id
        errorOnDuplicateFunction = False
        try:
            myMsbClient.addFunction(
                same_function_id,
                function_name,
                function_description,
                function_dataformat,
                printMsg,
                isArray,
                responseEvents,
            )
        except Exception:
            errorOnDuplicateFunction = True

        # 3. ASSERT
        self.assertEqual(errorOnDuplicateFunction, True)

    def test_doNotAddClientFunctionPerSingleParamWithInvalidDatatype(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        function_id = str(uuid.uuid4())[-6:]
        function_name = "FUNC " + function_id
        function_description = "FUNC Description " + function_id
        function_dataformat = "blablub"
        isArray = True
        responseEvents = []

        # 2. ACT
        errorOnWrongDatatype = False
        try:
            myMsbClient.addFunction(
                function_id,
                function_name,
                function_description,
                function_dataformat,
                printMsg,
                isArray,
                responseEvents,
            )
        except Exception as error:
            logging.error(error)
            errorOnWrongDatatype = True

        # 3. ASSERT
        self.assertEqual(errorOnWrongDatatype, True)

    def test_doNotAddClientFunctionPerFunctionObjectWithInvalidDatatype(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        function_id = str(uuid.uuid4())[-6:]
        function_name = "FUNC " + function_id
        function_description = "FUNC Description " + function_id
        function_dataformat = "blablub"
        isArray = False
        responseEvents = []

        # 2. ACT
        errorOnWrongDatatype = False
        try:
            function = Function(
                function_id,
                function_name,
                function_description,
                function_dataformat,
                printMsg,
                isArray,
                responseEvents,
            )
            myMsbClient.addFunction(function)
        except Exception as error:
            logging.error(error)
            errorOnWrongDatatype = True

        # 3. ASSERT
        self.assertEqual(errorOnWrongDatatype, True)

    def test_addClientFunctionPerSingleParamsWithSelfDefinedComplexObject(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        function_id = str(uuid.uuid4())[-6:]
        function_name = "FUNC " + function_id
        function_description = "FUNC Description " + function_id
        isArray = False
        responseEvents = []

        complexObject_name_1 = "ComplexObject1"
        complexObject_property_name_1 = "megaprop"
        complexObject_isArray_1 = False
        complexObject_name_2 = "ComplexObject2"
        complexObject_property_name_2 = "superprop"
        complexObject_datatype_2 = "int32"
        complexObject_isArray_2 = True

        complexObject_1 = ComplexDataFormat(complexObject_name_1)
        complexObject_2 = ComplexDataFormat(complexObject_name_2)
        complexObject_2.addProperty(
            complexObject_property_name_2,
            complexObject_datatype_2,
            complexObject_isArray_2
        )
        complexObject_1.addProperty(
            complexObject_property_name_1,
            complexObject_2,
            complexObject_isArray_1
        )

        # 2. ACT
        myMsbClient.addFunction(
            function_id,
            function_name,
            function_description,
            complexObject_1,
            printMsg,
            isArray,
            responseEvents,
        )
        # 3. ASSERT
        self.assertEqual(myMsbClient.functions[function_id].functionId, function_id)
        self.assertEqual(myMsbClient.functions[function_id].name, function_name)
        self.assertEqual(myMsbClient.functions[function_id].description, function_description)
        self.assertEqual(myMsbClient.functions[function_id].isArray, isArray)
        self.assertEqual(myMsbClient.functions[function_id].implementation, printMsg)
        self.assertEqual(myMsbClient.functions[function_id].dataFormat[complexObject_name_1]["type"], "object")
        self.assertEqual(myMsbClient.functions[function_id].dataFormat[complexObject_name_1]
                         ["properties"][complexObject_property_name_1]["$ref"],
                         "#/definitions/" + complexObject_name_2)
        self.assertEqual(myMsbClient.functions[function_id].dataFormat[complexObject_name_2]["type"], "object")
        self.assertEqual(myMsbClient.functions[function_id].dataFormat[complexObject_name_2]
                         ["properties"][complexObject_property_name_2]["type"], "array")
        self.assertEqual(myMsbClient.functions[function_id].dataFormat[complexObject_name_2]
                         ["properties"][complexObject_property_name_2]["items"]["type"], "integer")
        self.assertEqual(myMsbClient.functions[function_id].dataFormat[complexObject_name_2]
                         ["properties"][complexObject_property_name_2]["items"]["format"], complexObject_datatype_2)
        self.assertEqual(myMsbClient.functions[function_id].dataFormat["dataObject"]["type"], "object")
        self.assertEqual(myMsbClient.functions[function_id].dataFormat["dataObject"]
                         ["$ref"], "#/definitions/" + complexObject_name_1)

    def test_addClientFunctionPerSingleParamsWithSelfDefinedComplexObjectAsArray(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        function_id = str(uuid.uuid4())[-6:]
        function_name = "FUNC " + function_id
        function_description = "FUNC Description " + function_id
        isArray = True
        responseEvents = []

        complexObject_name_1 = "FuncComplexObject1"
        complexObject_property_name_1 = "megaprop"
        complexObject_isArray_1 = True
        complexObject_name_2 = "FuncComplexObject2"
        complexObject_property_name_2 = "superprop"
        complexObject_datatype_2 = "int32"
        complexObject_isArray_2 = False

        complexObject_1 = ComplexDataFormat(complexObject_name_1)
        complexObject_2 = ComplexDataFormat(complexObject_name_2)
        complexObject_2.addProperty(
            complexObject_property_name_2,
            complexObject_datatype_2,
            complexObject_isArray_2
        )
        complexObject_1.addProperty(
            complexObject_property_name_1,
            complexObject_2,
            complexObject_isArray_1
        )

        # 2. ACT
        myMsbClient.addFunction(
            function_id,
            function_name,
            function_description,
            complexObject_1,
            printMsg,
            isArray,
            responseEvents,
        )
        # 3. ASSERT
        self.assertEqual(myMsbClient.functions[function_id].functionId, function_id)
        self.assertEqual(myMsbClient.functions[function_id].name, function_name)
        self.assertEqual(myMsbClient.functions[function_id].description, function_description)
        self.assertEqual(myMsbClient.functions[function_id].isArray, isArray)
        self.assertEqual(myMsbClient.functions[function_id].implementation, printMsg)
        self.assertEqual(myMsbClient.functions[function_id].dataFormat[complexObject_name_1]["type"], "object")
        self.assertEqual(myMsbClient.functions[function_id].dataFormat[complexObject_name_1]
                         ["properties"][complexObject_property_name_1]["type"], "array")
        self.assertEqual(myMsbClient.functions[function_id].dataFormat[complexObject_name_1]
                         ["properties"][complexObject_property_name_1]["items"]["$ref"],
                         "#/definitions/" + complexObject_name_2)
        self.assertEqual(myMsbClient.functions[function_id].dataFormat[complexObject_name_2]["type"], "object")
        self.assertEqual(myMsbClient.functions[function_id].dataFormat[complexObject_name_2]
                         ["properties"][complexObject_property_name_2]["type"], "integer")
        self.assertEqual(myMsbClient.functions[function_id].dataFormat[complexObject_name_2]
                         ["properties"][complexObject_property_name_2]["format"], complexObject_datatype_2)
        self.assertEqual(myMsbClient.functions[function_id].dataFormat["dataObject"]["type"], "array")
        self.assertEqual(myMsbClient.functions[function_id].dataFormat["dataObject"]
                         ["items"]["$ref"], "#/definitions/" + complexObject_name_1)

    def test_addClientEventPerSingleParamsWithSelfDefinedComplexObjectAsJsonString(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        function_id = str(uuid.uuid4())[-6:]
        function_name = "FUNC " + function_id
        function_description = "FUNC Description " + function_id
        isArray = False
        responseEvents = []

        complexDataFormatAsJsonString = {
            "Member": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "status": {
                        "enum": ["present", "absent"],
                        "type": "string"
                    }
                }
            },
            "Team": {
                "type": "object",
                "properties": {
                    "staff": {
                        "type": "array",
                        "items": {
                            "$ref": "#/definitions/Member"
                        }
                    }
                }
            },
            "dataObject": {
                "$ref": "#/definitions/Team"
            }
        }

        # 2. ACT
        myMsbClient.addFunction(
            function_id,
            function_name,
            function_description,
            complexDataFormatAsJsonString,
            printMsg,
            isArray,
            responseEvents,
        )

        # 3. ASSERT
        self.assertEqual(myMsbClient.functions[function_id].functionId, function_id)
        self.assertEqual(myMsbClient.functions[function_id].name, function_name)
        self.assertEqual(myMsbClient.functions[function_id].description, function_description)
        self.assertEqual(myMsbClient.functions[function_id].isArray, isArray)
        self.assertEqual(myMsbClient.functions[function_id].implementation, printMsg)
        self.assertEqual(myMsbClient.functions[function_id].dataFormat["Team"]["type"], "object")
        self.assertEqual(myMsbClient.functions[function_id].dataFormat["Team"]
                         ["properties"]["staff"]["type"], "array")
        self.assertEqual(myMsbClient.functions[function_id].dataFormat["Team"]
                         ["properties"]["staff"]["items"]["$ref"],
                         "#/definitions/" + "Member")
        self.assertEqual(myMsbClient.functions[function_id].dataFormat["Member"]["type"], "object")
        self.assertEqual(myMsbClient.functions[function_id].dataFormat["Member"]
                         ["properties"]["name"]["type"], "string")
        self.assertEqual(myMsbClient.functions[function_id].dataFormat["Member"]
                         ["properties"]["status"]["type"], "string")
        self.assertEqual(myMsbClient.functions[function_id].dataFormat["Member"]
                         ["properties"]["status"]["enum"], ["present", "absent"])
        self.assertEqual(myMsbClient.functions[function_id].dataFormat["dataObject"]["type"], "object")
        self.assertEqual(myMsbClient.functions[function_id].dataFormat["dataObject"]
                         ["$ref"], "#/definitions/" + "Team")


class TestMSBClientCreateClientEvents(unittest.TestCase):
    """
    Test the creation of client events
    """

    def test_addClientEventPerSingleParam(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_dataformat = "string"
        event_priority = 1
        isArray = False

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            event_dataformat,
            event_priority,
            isArray,
        )

        # 3. ASSERT
        self.assertEqual(myMsbClient.events[event_id].eventId, event_id)
        self.assertEqual(myMsbClient.events[event_id].name, event_name)
        self.assertEqual(myMsbClient.events[event_id].description, event_description)
        self.assertEqual(myMsbClient.events[event_id].isArray, isArray)
        self.assertEqual(myMsbClient.events[event_id].dataFormat["dataObject"]["type"], event_dataformat)
        self.assertEqual(myMsbClient.events[event_id].priority, event_priority)

    def test_addClientEventPerEventObject(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_dataformat = bool
        event_priority = 1
        isArray = False

        # 2. ACT
        event = Event(
            event_id,
            event_name,
            event_description,
            event_dataformat,
            event_priority,
            isArray,
        )
        myMsbClient.addEvent(event)

        # 3. ASSERT
        self.assertEqual(myMsbClient.events[event_id].eventId, event_id)
        self.assertEqual(myMsbClient.events[event_id].name, event_name)
        self.assertEqual(myMsbClient.events[event_id].description, event_description)
        self.assertEqual(myMsbClient.events[event_id].isArray, isArray)
        self.assertEqual(myMsbClient.events[event_id].dataFormat["dataObject"]["type"], "boolean")
        self.assertEqual(myMsbClient.events[event_id].priority, event_priority)

    def test_addClientEventPerSingleParamAsJsonString(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_dataformat = '{ "type": "number",  "format": "double" }'
        event_priority = 1
        isArray = False

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            event_dataformat,
            event_priority,
            isArray,
        )

        # 3. ASSERT
        self.assertEqual(myMsbClient.events[event_id].eventId, event_id)
        self.assertEqual(myMsbClient.events[event_id].name, event_name)
        self.assertEqual(myMsbClient.events[event_id].description, event_description)
        self.assertEqual(myMsbClient.events[event_id].isArray, isArray)
        self.assertEqual(myMsbClient.events[event_id].dataFormat["dataObject"]["type"], "number")
        self.assertEqual(myMsbClient.events[event_id].dataFormat["dataObject"]["format"], "double")
        self.assertEqual(myMsbClient.events[event_id].priority, event_priority)

    def test_addClientEventPerSinleParamAsArray(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_dataformat = DataType.DATETIME
        event_priority = 1
        isArray = True

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            event_dataformat,
            event_priority,
            isArray,
        )

        # 3. ASSERT
        self.assertEqual(myMsbClient.events[event_id].eventId, event_id)
        self.assertEqual(myMsbClient.events[event_id].name, event_name)
        self.assertEqual(myMsbClient.events[event_id].description, event_description)
        self.assertEqual(myMsbClient.events[event_id].isArray, isArray)
        self.assertEqual(myMsbClient.events[event_id].dataFormat["dataObject"]["type"], "array")
        self.assertEqual(myMsbClient.events[event_id].dataFormat["dataObject"]["items"]["type"], "string")
        self.assertEqual(myMsbClient.events[event_id].dataFormat["dataObject"]["items"]["format"], "date-time")
        self.assertEqual(myMsbClient.events[event_id].priority, event_priority)

    def test_addClientEventPerSinleParamWithNoPayload(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_dataformat = None
        event_priority = 1
        isArray = False

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            event_dataformat,
            event_priority,
            isArray,
        )

        # 3. ASSERT
        self.assertEqual(myMsbClient.events[event_id].eventId, event_id)
        self.assertEqual(myMsbClient.events[event_id].name, event_name)
        self.assertEqual(myMsbClient.events[event_id].description, event_description)
        self.assertEqual(myMsbClient.events[event_id].isArray, isArray)
        self.assertIsNone(myMsbClient.events[event_id].dataFormat)
        self.assertEqual(myMsbClient.events[event_id].priority, event_priority)

    def test_doNotAddDuplicateClientEvent(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_dataformat = None
        event_priority = 1
        isArray = False

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            event_dataformat,
            event_priority,
            isArray,
        )
        event_id_already_used = event_id
        errorOnDuplicateEvent = False
        try:
            myMsbClient.addEvent(
                event_id_already_used,
                event_name,
                event_description,
                event_dataformat,
                event_priority,
                isArray,
            )
        except Exception as error:
            logging.error(error)
            errorOnDuplicateEvent = True

        # 3. ASSERT
        self.assertEqual(errorOnDuplicateEvent, True)

    def test_doNotAddClientEventWithInvalidDatatype(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_dataformat = "InvalidDT"
        event_priority = 1
        isArray = True

        # 2. ACT
        errorOnInvalidDatatype = False
        try:
            myMsbClient.addEvent(
                event_id,
                event_name,
                event_description,
                event_dataformat,
                event_priority,
                isArray,
            )
        except Exception as error:
            logging.error(error)
            errorOnInvalidDatatype = True

        # 3. ASSERT
        self.assertEqual(errorOnInvalidDatatype, True)

    def test_addClientEventPerSingleParamsWithSelfDefinedComplexObject(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_priority = 1
        isArray = False

        complexObject_name_1 = "ComplexObject1"
        complexObject_property_name_1 = "megaprop"
        complexObject_isArray_1 = False
        complexObject_name_2 = "ComplexObject2"
        complexObject_property_name_2 = "superprop"
        complexObject_datatype_2 = "int32"
        complexObject_isArray_2 = True

        complexObject_1 = ComplexDataFormat(complexObject_name_1)
        complexObject_2 = ComplexDataFormat(complexObject_name_2)
        complexObject_2.addProperty(
            complexObject_property_name_2,
            complexObject_datatype_2,
            complexObject_isArray_2
        )
        complexObject_1.addProperty(
            complexObject_property_name_1,
            complexObject_2,
            complexObject_isArray_1
        )

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            complexObject_1,
            event_priority,
            isArray,
        )
        # 3. ASSERT
        self.assertEqual(myMsbClient.events[event_id].eventId, event_id)
        self.assertEqual(myMsbClient.events[event_id].name, event_name)
        self.assertEqual(myMsbClient.events[event_id].description, event_description)
        self.assertEqual(myMsbClient.events[event_id].isArray, isArray)
        self.assertEqual(myMsbClient.events[event_id].priority, event_priority)
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_1]["type"], "object")
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_1]
                         ["properties"][complexObject_property_name_1]["$ref"],
                         "#/definitions/" + complexObject_name_2)
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_2]["type"], "object")
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_2]
                         ["properties"][complexObject_property_name_2]["type"], "array")
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_2]
                         ["properties"][complexObject_property_name_2]["items"]["type"], "integer")
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_2]["properties"]
                         [complexObject_property_name_2]["items"]["format"], complexObject_datatype_2)
        self.assertEqual(myMsbClient.events[event_id].dataFormat["dataObject"]["type"], "object")
        self.assertEqual(myMsbClient.events[event_id].dataFormat["dataObject"]
                         ["$ref"], "#/definitions/" + complexObject_name_1)

    def test_addClientEventPerSingleParamsWithSelfDefinedComplexObjectAsArray(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_priority = 1
        isArray = True

        complexObject_name_1 = "ComplexObject1"
        complexObject_property_name_1 = "megaprop"
        complexObject_isArray_1 = True
        complexObject_name_2 = "ComplexObject2"
        complexObject_property_name_2 = "superprop"
        complexObject_datatype_2 = "int32"
        complexObject_isArray_2 = False

        complexObject_1 = ComplexDataFormat(complexObject_name_1)
        complexObject_2 = ComplexDataFormat(complexObject_name_2)
        complexObject_2.addProperty(
            complexObject_property_name_2,
            complexObject_datatype_2,
            complexObject_isArray_2
        )
        complexObject_1.addProperty(
            complexObject_property_name_1,
            complexObject_2,
            complexObject_isArray_1
        )

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            complexObject_1,
            event_priority,
            isArray,
        )
        # 3. ASSERT
        logging.debug("\nEVENT " + str(myMsbClient.events[event_id].dataFormat))
        self.assertEqual(myMsbClient.events[event_id].eventId, event_id)
        self.assertEqual(myMsbClient.events[event_id].name, event_name)
        self.assertEqual(myMsbClient.events[event_id].description, event_description)
        self.assertEqual(myMsbClient.events[event_id].isArray, isArray)
        self.assertEqual(myMsbClient.events[event_id].priority, event_priority)
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_1]["type"], "object")
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_1]
                         ["properties"][complexObject_property_name_1]["type"], "array")
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_1]
                         ["properties"][complexObject_property_name_1]["items"]["$ref"],
                         "#/definitions/" + complexObject_name_2)
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_2]["type"], "object")
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_2]
                         ["properties"][complexObject_property_name_2]["type"], "integer")
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_2]
                         ["properties"][complexObject_property_name_2]["format"], complexObject_datatype_2)
        self.assertEqual(myMsbClient.events[event_id].dataFormat["dataObject"]["type"], "array")
        self.assertEqual(myMsbClient.events[event_id].dataFormat["dataObject"]
                         ["items"]["$ref"], "#/definitions/" + complexObject_name_1)

    def test_addClientEventPerSingleParamsWith4LayerSelfDefinedComplexObject(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_priority = 1
        isArray = False

        complexObject_name_1 = "ComplexObject1"
        complexObject_property_name_1 = "megaprop"
        complexObject_isArray_1 = False
        complexObject_name_2 = "ComplexObject2"
        complexObject_property_name_2 = "superprop"
        complexObject_isArray_2 = True
        complexObject_name_3 = "ComplexObject3"
        complexObject_property_name_3 = "mediumprop"
        complexObject_isArray_3 = True
        complexObject_name_4 = "ComplexObject4"
        complexObject_property_name_4 = "prop"
        complexObject_datatype_4 = "int32"
        complexObject_isArray_4 = True

        complexObject_1 = ComplexDataFormat(complexObject_name_1)
        complexObject_2 = ComplexDataFormat(complexObject_name_2)
        complexObject_3 = ComplexDataFormat(complexObject_name_3)
        complexObject_4 = ComplexDataFormat(complexObject_name_4)
        complexObject_4.addProperty(
            complexObject_property_name_4,
            complexObject_datatype_4,
            complexObject_isArray_4
        )
        complexObject_3.addProperty(
            complexObject_property_name_3,
            complexObject_4,
            complexObject_isArray_3
        )
        complexObject_2.addProperty(
            complexObject_property_name_2,
            complexObject_3,
            complexObject_isArray_2
        )
        complexObject_1.addProperty(
            complexObject_property_name_1,
            complexObject_2,
            complexObject_isArray_1
        )

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            complexObject_1,
            event_priority,
            isArray,
        )
        # 3. ASSERT
        logging.debug("\nEVENT " + str(myMsbClient.events[event_id].dataFormat))
        self.assertEqual(myMsbClient.events[event_id].eventId, event_id)
        self.assertEqual(myMsbClient.events[event_id].name, event_name)
        self.assertEqual(myMsbClient.events[event_id].description, event_description)
        self.assertEqual(myMsbClient.events[event_id].isArray, isArray)
        self.assertEqual(myMsbClient.events[event_id].priority, event_priority)
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_1]["type"], "object")
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_1]
                         ["properties"][complexObject_property_name_1]["$ref"],
                         "#/definitions/" + complexObject_name_2)
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_2]["type"], "object")
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_2]
                         ["properties"][complexObject_property_name_2]["type"], "array")
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_2]
                         ["properties"][complexObject_property_name_2]["items"]["$ref"],
                         "#/definitions/" + complexObject_name_3)
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_3]["type"], "object")
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_3]
                         ["properties"][complexObject_property_name_3]["type"], "array")
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_3]
                         ["properties"][complexObject_property_name_3]["items"]["$ref"],
                         "#/definitions/" + complexObject_name_4)
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_4]["type"], "object")
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_4]
                         ["properties"][complexObject_property_name_4]["type"], "array")
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_4]
                         ["properties"][complexObject_property_name_4]["items"]["type"], "integer")
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_4]["properties"]
                         [complexObject_property_name_4]["items"]["format"], complexObject_datatype_4)
        self.assertEqual(myMsbClient.events[event_id].dataFormat["dataObject"]["type"], "object")
        self.assertEqual(myMsbClient.events[event_id].dataFormat["dataObject"]
                         ["$ref"], "#/definitions/" + complexObject_name_1)

    def test_addClientEventPerSingleParamsWith4LayerSelfDefinedComplexObjectAndRecursion(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_priority = 1
        isArray = False

        complexObject_name_1 = "ComplexObject1_B"
        complexObject_property_name_1 = "megaprop"
        complexObject_isArray_1 = False
        complexObject_name_2 = "ComplexObject2_B"
        complexObject_property_name_2 = "superprop"
        complexObject_isArray_2 = True
        complexObject_name_3 = "ComplexObject3_B"
        complexObject_property_name_3 = "mediumprop"
        complexObject_isArray_3 = True
        complexObject_property_name_3p2 = "recurseprop"
        complexObject_isArray_3p2 = True
        complexObject_name_4 = "ComplexObject4_B"
        complexObject_property_name_4 = "prop"
        complexObject_datatype_4 = "int32"
        complexObject_isArray_4 = True

        complexObject_1 = ComplexDataFormat(complexObject_name_1)
        complexObject_2 = ComplexDataFormat(complexObject_name_2)
        complexObject_3 = ComplexDataFormat(complexObject_name_3)
        complexObject_4 = ComplexDataFormat(complexObject_name_4)
        complexObject_4.addProperty(
            complexObject_property_name_4,
            complexObject_datatype_4,
            complexObject_isArray_4
        )
        complexObject_3.addProperty(
            complexObject_property_name_3,
            complexObject_4,
            complexObject_isArray_3
        )
        complexObject_3.addProperty(
            complexObject_property_name_3p2,
            complexObject_2,
            complexObject_isArray_3p2
        )
        complexObject_2.addProperty(
            complexObject_property_name_2,
            complexObject_3,
            complexObject_isArray_2
        )
        complexObject_1.addProperty(
            complexObject_property_name_1,
            complexObject_2,
            complexObject_isArray_1
        )
        logging.debug("\nComplex Object TEST: " + str(complexObject_3.dataFormat[complexObject_name_3]["properties"]))

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            complexObject_1,
            event_priority,
            isArray,
        )
        # 3. ASSERT
        logging.debug("\nEVENT REC" + str(myMsbClient.events[event_id].dataFormat))
        self.assertEqual(myMsbClient.events[event_id].eventId, event_id)
        self.assertEqual(myMsbClient.events[event_id].name, event_name)
        self.assertEqual(myMsbClient.events[event_id].description, event_description)
        self.assertEqual(myMsbClient.events[event_id].isArray, isArray)
        self.assertEqual(myMsbClient.events[event_id].priority, event_priority)
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_1]["type"], "object")
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_1]
                         ["properties"][complexObject_property_name_1]["$ref"],
                         "#/definitions/" + complexObject_name_2)
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_2]["type"], "object")
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_2]
                         ["properties"][complexObject_property_name_2]["type"], "array")
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_2]
                         ["properties"][complexObject_property_name_2]["items"]["$ref"],
                         "#/definitions/" + complexObject_name_3)
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_3]["type"], "object")
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_3]
                         ["properties"][complexObject_property_name_3]["type"], "array")
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_3]
                         ["properties"][complexObject_property_name_3]["items"]["$ref"],
                         "#/definitions/" + complexObject_name_4)
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_3]
                         ["properties"][complexObject_property_name_3p2]["type"], "array")
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_3]
                         ["properties"][complexObject_property_name_3p2]["items"]["$ref"],
                         "#/definitions/" + complexObject_name_2)
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_4]["type"], "object")
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_4]
                         ["properties"][complexObject_property_name_4]["type"], "array")
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_4]
                         ["properties"][complexObject_property_name_4]["items"]["type"], "integer")
        self.assertEqual(myMsbClient.events[event_id].dataFormat[complexObject_name_4]["properties"]
                         [complexObject_property_name_4]["items"]["format"], complexObject_datatype_4)
        self.assertEqual(myMsbClient.events[event_id].dataFormat["dataObject"]["type"], "object")
        self.assertEqual(myMsbClient.events[event_id].dataFormat["dataObject"]
                         ["$ref"], "#/definitions/" + complexObject_name_1)

    def test_addClientEventPerSingleParamsWithSelfDefinedComplexObjectAsJsonString(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_priority = 1
        isArray = False

        complexDataFormatAsJsonString = {
            "Member": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "status": {
                        "enum": ["present", "absent"],
                        "type": "string"
                    }
                }
            },
            "Team": {
                "type": "object",
                "properties": {
                    "staff": {
                        "type": "array",
                        "items": {
                            "$ref": "#/definitions/Member"
                        }
                    }
                }
            },
            "dataObject": {
                "$ref": "#/definitions/Team"
            }
        }

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            complexDataFormatAsJsonString,
            event_priority,
            isArray,
        )

        # 3. ASSERT
        logging.debug("\nEVENT JSON DataFormat" + str(myMsbClient.events[event_id].dataFormat))
        self.assertEqual(myMsbClient.events[event_id].eventId, event_id)
        self.assertEqual(myMsbClient.events[event_id].name, event_name)
        self.assertEqual(myMsbClient.events[event_id].description, event_description)
        self.assertEqual(myMsbClient.events[event_id].isArray, isArray)
        self.assertEqual(myMsbClient.events[event_id].priority, event_priority)
        self.assertEqual(myMsbClient.events[event_id].dataFormat["Team"]["type"], "object")
        self.assertEqual(myMsbClient.events[event_id].dataFormat["Team"]
                         ["properties"]["staff"]["type"], "array")
        self.assertEqual(myMsbClient.events[event_id].dataFormat["Team"]
                         ["properties"]["staff"]["items"]["$ref"],
                         "#/definitions/" + "Member")
        self.assertEqual(myMsbClient.events[event_id].dataFormat["Member"]["type"], "object")
        self.assertEqual(myMsbClient.events[event_id].dataFormat["Member"]
                         ["properties"]["name"]["type"], "string")
        self.assertEqual(myMsbClient.events[event_id].dataFormat["Member"]
                         ["properties"]["status"]["type"], "string")
        self.assertEqual(myMsbClient.events[event_id].dataFormat["Member"]
                         ["properties"]["status"]["enum"], ["present", "absent"])
        self.assertEqual(myMsbClient.events[event_id].dataFormat["dataObject"]["type"], "object")
        self.assertEqual(myMsbClient.events[event_id].dataFormat["dataObject"]
                         ["$ref"], "#/definitions/" + "Team")


class TestMSBClientCreateSelfDescription(unittest.TestCase):
    """
    Test the creation of the self description
    """

    def test_getSelfDescriptionBasic(self):
        # 1. ARRANGE
        # 2. ACT
        myMsbClient = MsbClient(
            SERVICE_TYPE,
            SO_UUID,
            SO_NAME,
            SO_DESCRIPTION,
            SO_TOKEN
        )

        # 3. ASSERT
        selfDescription = myMsbClient.getSelfDescription()
        self.assertEqual(selfDescription["uuid"], SO_UUID)
        self.assertEqual(selfDescription["name"], SO_NAME)
        self.assertEqual(selfDescription["description"], SO_DESCRIPTION)
        self.assertEqual(selfDescription["token"], SO_TOKEN)

    def test_getSelfDescriptionWithConfigrationParameters(self):
        # 1. ARRANGE
        param_name_1 = "testParam1"
        param_value_1 = True
        param_datatype_1 = bool

        param_name_2 = "testParam2"
        param_value_2 = "StringValue"
        param_datatype_2 = str

        param_name_3 = "testParam3"
        param_value_3 = 1000
        param_datatype_3 = "int32"

        # 2. ACT
        myMsbClient = MsbClient()
        myMsbClient.addConfigParameter(param_name_1, param_value_1, param_datatype_1)
        myMsbClient.addConfigParameter(param_name_2, param_value_2, param_datatype_2)
        myMsbClient.addConfigParameter(param_name_3, param_value_3, param_datatype_3)

        # 3. ASSERT
        selfDescription = myMsbClient.getSelfDescription()
        self.assertEqual(selfDescription["configuration"]["parameters"][param_name_1]["value"], param_value_1)
        self.assertEqual(selfDescription["configuration"]["parameters"][param_name_1]["type"], "BOOLEAN")
        self.assertEqual(selfDescription["configuration"]["parameters"][param_name_2]["value"], param_value_2)
        self.assertEqual(selfDescription["configuration"]["parameters"][param_name_2]["type"], "STRING")
        self.assertEqual(selfDescription["configuration"]["parameters"][param_name_3]["value"], param_value_3)
        self.assertEqual(selfDescription["configuration"]["parameters"][param_name_3]["type"], "INTEGER")
        self.assertEqual(selfDescription["configuration"]["parameters"][param_name_3]["format"], "INT32")

    def test_getSelfDescriptionWithFunctions(self):
        # 1. ARRANGE
        function_id = str(uuid.uuid4())[-6:]
        function_name = "FUNC " + function_id
        function_description = "FUNC Description " + function_id
        function_dataformat = None
        isArray = True
        responseEvents = []

        # 2. ACT
        myMsbClient = MsbClient()
        myMsbClient.addFunction(
            function_id,
            function_name,
            function_description,
            function_dataformat,
            printMsg,
            isArray,
            responseEvents,
        )

        # 3. ASSERT
        selfDescription = myMsbClient.getSelfDescription()
        self.assertEqual(selfDescription["functions"][0]["functionId"], function_id)
        self.assertEqual(selfDescription["functions"][0]["name"], function_name)
        self.assertEqual(selfDescription["functions"][0]["description"], function_description)
        self.assertNotIn(selfDescription["functions"][0], ["dataFormat"])
        self.assertNotIn(selfDescription["functions"][0], ["responseEvents"])
        self.assertNotIn(selfDescription["functions"][0], ["implementation"])

    def test_getSelfDescriptionWithFunctions2(self):
        # 1. ARRANGE
        event_1_id = str(uuid.uuid4())[-6:]
        event_1_name = "EVENT " + event_1_id
        event_1_description = "EVENT Description " + event_1_id
        event_1_dataformat = None
        event_1_priority = 2
        event_1_isArray = False

        function_id = str(uuid.uuid4())[-6:]
        function_name = "FUNC " + function_id
        function_description = "FUNC Description " + function_id
        function_dataformat = DataType.STRING
        isArray = True
        responseEvents = [event_1_id]

        # 2. ACT
        myMsbClient = MsbClient()
        myMsbClient.addEvent(
            event_1_id,
            event_1_name,
            event_1_description,
            event_1_dataformat,
            event_1_priority,
            event_1_isArray
        )
        myMsbClient.addFunction(
            function_id,
            function_name,
            function_description,
            function_dataformat,
            printMsg,
            isArray,
            responseEvents,
        )

        # 3. ASSERT
        selfDescription = myMsbClient.getSelfDescription()
        self.assertEqual(selfDescription["functions"][0]["functionId"], function_id)
        self.assertEqual(selfDescription["functions"][0]["name"], function_name)
        self.assertEqual(selfDescription["functions"][0]["description"], function_description)
        self.assertEqual(selfDescription["functions"][0]["dataFormat"]["dataObject"]["type"], "array")
        self.assertEqual(selfDescription["functions"][0]["dataFormat"]["dataObject"]
                         ["items"]["type"], "string")
        self.assertEqual(len(selfDescription["functions"][0]["responseEvents"]), len(responseEvents))
        self.assertNotIn(selfDescription["functions"][0], ["implementation"])

    def test_getSelfDescriptionWithEvents(self):
        # 1. ARRANGE
        event_1_id = str(uuid.uuid4())[-6:]
        event_1_name = "EVENT " + event_1_id
        event_1_description = "EVENT Description " + event_1_id
        event_1_dataformat = DataType.INT32
        event_1_priority = 2
        event_1_isArray = True

        event_2_id = str(uuid.uuid4())[-6:]
        event_2_name = "EVENT " + event_2_id
        event_2_description = "EVENT Description " + event_2_id
        event_2_dataformat = None
        event_2_priority = 2
        event_2_isArray = False

        # 2. ACT
        myMsbClient = MsbClient()
        myMsbClient.addEvent(
            event_1_id,
            event_1_name,
            event_1_description,
            event_1_dataformat,
            event_1_priority,
            event_1_isArray
        )
        myMsbClient.addEvent(
            event_2_id,
            event_2_name,
            event_2_description,
            event_2_dataformat,
            event_2_priority,
            event_2_isArray
        )

        # 3. ASSERT
        selfDescription = myMsbClient.getSelfDescription()

        """"
        Fails randomly because events list in selfDescription is list while events property of MsbClient is Dict
        therefore first Element in list depends on alpabetical order of event ID than insertation sequence of events

        Therefore read events with following command than using selfDescription["events"][X]
        """

        selfDesc_event1 = next((event for event in selfDescription["events"] if event["eventId"] == event_1_id), None)
        selfDesc_event2 = next((event for event in selfDescription["events"] if event["eventId"] == event_2_id), None)

        self.assertEqual(selfDesc_event1["eventId"], event_1_id)
        self.assertEqual(selfDesc_event1["name"], event_1_name)
        self.assertEqual(selfDesc_event1["description"], event_1_description)
        self.assertEqual(selfDesc_event1["dataFormat"]["dataObject"]["type"], "array")
        self.assertEqual(selfDesc_event1["dataFormat"]["dataObject"]
                         ["items"]["type"], "integer")
        self.assertEqual(selfDesc_event1["dataFormat"]["dataObject"]
                         ["items"]["format"], "int32")
        self.assertEqual(selfDesc_event2["eventId"], event_2_id)
        self.assertEqual(selfDesc_event2["name"], event_2_name)
        self.assertEqual(selfDesc_event2["description"], event_2_description)
        self.assertNotIn(selfDesc_event2, ["dataFormat"])

    def test_getSelfDescriptionWithComplexObject(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_priority = 1
        isArray = False

        complexObject_name_1 = "ComplexObject1"
        complexObject_property_name_1 = "megaprop"
        complexObject_isArray_1 = False
        complexObject_name_2 = "ComplexObject2"
        complexObject_property_name_2 = "superprop"
        complexObject_isArray_2 = True
        complexObject_name_3 = "ComplexObject3"
        complexObject_property_name_3 = "mediumprop"
        complexObject_isArray_3 = True
        complexObject_name_4 = "ComplexObject4"
        complexObject_property_name_4 = "prop"
        complexObject_datatype_4 = "int32"
        complexObject_isArray_4 = True

        complexObject_1 = ComplexDataFormat(complexObject_name_1)
        complexObject_2 = ComplexDataFormat(complexObject_name_2)
        complexObject_3 = ComplexDataFormat(complexObject_name_3)
        complexObject_4 = ComplexDataFormat(complexObject_name_4)
        complexObject_4.addProperty(
            complexObject_property_name_4,
            complexObject_datatype_4,
            complexObject_isArray_4
        )
        complexObject_3.addProperty(
            complexObject_property_name_3,
            complexObject_4,
            complexObject_isArray_3
        )
        complexObject_2.addProperty(
            complexObject_property_name_2,
            complexObject_3,
            complexObject_isArray_2
        )
        complexObject_1.addProperty(
            complexObject_property_name_1,
            complexObject_2,
            complexObject_isArray_1
        )

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            complexObject_1,
            event_priority,
            isArray,
        )

        # 3. ASSERT
        selfDescription = myMsbClient.getSelfDescription()
        selfDesc_event1 = next((event for event in selfDescription["events"] if event["eventId"] == event_id), None)

        self.assertEqual(selfDesc_event1["eventId"], event_id)
        self.assertEqual(selfDesc_event1["name"], event_name)
        self.assertEqual(selfDesc_event1["description"], event_description)
        self.assertEqual(selfDesc_event1["dataFormat"][complexObject_name_1]
                         ["properties"][complexObject_property_name_1]["$ref"],
                         "#/definitions/" + complexObject_name_2)
        self.assertEqual(selfDesc_event1["dataFormat"][complexObject_name_2]["type"], "object")
        self.assertEqual(selfDesc_event1["dataFormat"][complexObject_name_2]
                         ["properties"][complexObject_property_name_2]["type"], "array")
        self.assertEqual(selfDesc_event1["dataFormat"][complexObject_name_2]
                         ["properties"][complexObject_property_name_2]["items"]["$ref"],
                         "#/definitions/" + complexObject_name_3)
        self.assertEqual(selfDesc_event1["dataFormat"][complexObject_name_3]["type"], "object")
        self.assertEqual(selfDesc_event1["dataFormat"][complexObject_name_3]
                         ["properties"][complexObject_property_name_3]["type"], "array")
        self.assertEqual(selfDesc_event1["dataFormat"][complexObject_name_3]
                         ["properties"][complexObject_property_name_3]["items"]["$ref"],
                         "#/definitions/" + complexObject_name_4)
        self.assertEqual(selfDesc_event1["dataFormat"][complexObject_name_4]["type"], "object")
        self.assertEqual(selfDesc_event1["dataFormat"][complexObject_name_4]
                         ["properties"][complexObject_property_name_4]["type"], "array")
        self.assertEqual(selfDesc_event1["dataFormat"][complexObject_name_4]
                         ["properties"][complexObject_property_name_4]["items"]["type"], "integer")
        self.assertEqual(selfDesc_event1["dataFormat"][complexObject_name_4]["properties"]
                         [complexObject_property_name_4]["items"]["format"], complexObject_datatype_4)
        self.assertEqual(selfDesc_event1["dataFormat"]["dataObject"]["type"], "object")
        self.assertEqual(selfDesc_event1["dataFormat"]["dataObject"]["$ref"], "#/definitions/" + complexObject_name_1)

    def test_getSelfDescriptionWithComplexObjectAsJsonString(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_priority = 1
        isArray = False

        complexDataFormatAsJsonString = {
            "Member": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "status": {
                        "enum": ["present", "absent"],
                        "type": "string"
                    }
                }
            },
            "Team": {
                "type": "object",
                "properties": {
                    "staff": {
                        "type": "array",
                        "items": {
                            "$ref": "#/definitions/Member"
                        }
                    }
                }
            },
            "dataObject": {
                "$ref": "#/definitions/Team"
            }
        }

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            complexDataFormatAsJsonString,
            event_priority,
            isArray,
        )

        # 3. ASSERT
        selfDescription = myMsbClient.getSelfDescription()
        selfDesc_event1 = next((event for event in selfDescription["events"] if event["eventId"] == event_id), None)

        self.assertEqual(selfDesc_event1["eventId"], event_id)
        self.assertEqual(selfDesc_event1["name"], event_name)
        self.assertEqual(selfDesc_event1["description"], event_description)
        self.assertEqual(selfDesc_event1["dataFormat"]["Team"]["type"], "object")
        self.assertEqual(selfDesc_event1["dataFormat"]["Team"]
                         ["properties"]["staff"]["type"], "array")
        self.assertEqual(selfDesc_event1["dataFormat"]["Team"]
                         ["properties"]["staff"]["items"]["$ref"],
                         "#/definitions/" + "Member")
        self.assertEqual(selfDesc_event1["dataFormat"]["Member"]["type"], "object")
        self.assertEqual(selfDesc_event1["dataFormat"]["Member"]
                         ["properties"]["name"]["type"], "string")
        self.assertEqual(selfDesc_event1["dataFormat"]["Member"]
                         ["properties"]["status"]["type"], "string")
        self.assertEqual(selfDesc_event1["dataFormat"]["Member"]
                         ["properties"]["status"]["enum"], ["present", "absent"])
        self.assertEqual(selfDesc_event1["dataFormat"]["dataObject"]["type"], "object")
        self.assertEqual(selfDesc_event1["dataFormat"]["dataObject"]
                         ["$ref"], "#/definitions/" + "Team")


class TestMSBClientEventValueValidation(unittest.TestCase):
    """
    Test the creation of the self description
    """

    def test_validateValueSimpleString(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_dataformat = str
        event_value = "TestString"
        event_priority = 1
        isArray = False

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            event_dataformat,
            event_priority,
            isArray,
        )

        # 3. ASSERT
        df = myMsbClient.events[event_id].df
        dataFormat = myMsbClient.events[event_id].dataFormat
        self.assertEqual(MsbClient.validateValueForDataFormat(event_value, df, dataFormat, isArray), True)

    def test_validateValueSimpleString_INVALID(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_dataformat = str
        event_value = 84
        event_priority = 1
        isArray = False

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            event_dataformat,
            event_priority,
            isArray,
        )

        # 3. ASSERT
        df = myMsbClient.events[event_id].df
        dataFormat = myMsbClient.events[event_id].dataFormat
        self.assertEqual(MsbClient.validateValueForDataFormat(event_value, df, dataFormat, isArray), False)

    def test_validateValueSimpleInteger(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_dataformat = DataType.INT32
        event_value = 55
        event_priority = 1
        isArray = False

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            event_dataformat,
            event_priority,
            isArray,
        )

        # 3. ASSERT
        df = myMsbClient.events[event_id].df
        dataFormat = myMsbClient.events[event_id].dataFormat
        self.assertEqual(MsbClient.validateValueForDataFormat(event_value, df, dataFormat, isArray), True)

    def test_validateValueSimpleInteger_INVALID(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_dataformat = int
        event_value = "TestString"
        event_priority = 1
        isArray = False

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            event_dataformat,
            event_priority,
            isArray,
        )

        # 3. ASSERT
        df = myMsbClient.events[event_id].df
        dataFormat = myMsbClient.events[event_id].dataFormat
        self.assertEqual(MsbClient.validateValueForDataFormat(event_value, df, dataFormat, isArray), False)

    def test_validateValueSimpleNumber(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_dataformat = DataType.FLOAT
        event_value = 55.3
        event_priority = 1
        isArray = False

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            event_dataformat,
            event_priority,
            isArray,
        )

        # 3. ASSERT
        df = myMsbClient.events[event_id].df
        dataFormat = myMsbClient.events[event_id].dataFormat
        self.assertEqual(MsbClient.validateValueForDataFormat(event_value, df, dataFormat, isArray), True)

    def test_validateValueSimpleNumber_INVALID(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_dataformat = DataType.FLOAT
        event_value = 12
        event_priority = 1
        isArray = False

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            event_dataformat,
            event_priority,
            isArray,
        )

        # 3. ASSERT
        df = myMsbClient.events[event_id].df
        dataFormat = myMsbClient.events[event_id].dataFormat
        self.assertEqual(MsbClient.validateValueForDataFormat(event_value, df, dataFormat, isArray), False)

    def test_validateValueSimpleDateTime(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_dataformat = DataType.DATETIME
        event_value = datetime.datetime.now()
        event_priority = 1
        isArray = False

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            event_dataformat,
            event_priority,
            isArray,
        )

        # 3. ASSERT
        df = myMsbClient.events[event_id].df
        dataFormat = myMsbClient.events[event_id].dataFormat
        self.assertEqual(MsbClient.validateValueForDataFormat(event_value, df, dataFormat, isArray), True)

    def test_validateValueSimpleDateTime_INVALID(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_dataformat = DataType.DATETIME
        event_value = "sdfsdfsdf"
        event_priority = 1
        isArray = False

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            event_dataformat,
            event_priority,
            isArray,
        )

        # 3. ASSERT
        df = myMsbClient.events[event_id].df
        dataFormat = myMsbClient.events[event_id].dataFormat
        self.assertEqual(MsbClient.validateValueForDataFormat(event_value, df, dataFormat, isArray), False)

    def test_validateValueSimpleByteString(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_dataformat = DataType.BYTE
        event_value = b"Bytes objects are immutable sequences of single bytes"
        event_priority = 1
        isArray = False

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            event_dataformat,
            event_priority,
            isArray,
        )

        # 3. ASSERT
        df = myMsbClient.events[event_id].df
        dataFormat = myMsbClient.events[event_id].dataFormat
        self.assertEqual(MsbClient.validateValueForDataFormat(event_value, df, dataFormat, isArray), True)

    def test_validateValueSimpleByteString_INVALID(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_dataformat = DataType.BYTE
        event_value = "sdfsdfsdf"
        event_priority = 1
        isArray = False

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            event_dataformat,
            event_priority,
            isArray
        )

        # 3. ASSERT
        """
        If test is done with Python 2 it is not possible to fulfill the test because technically it is not possible
        to distinguish between a string and a bytestring
        """
        if sys.version_info.major == 2:
            self.assertEqual(True, True)
        else:
            df = myMsbClient.events[event_id].df
            dataFormat = myMsbClient.events[event_id].dataFormat
            self.assertEqual(MsbClient.validateValueForDataFormat(event_value, df, dataFormat, isArray), False)

    def test_validateValueSimpleStringArray(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_dataformat = str
        event_value = ["Hello", "World", "!"]
        event_priority = 1
        isArray = True

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            event_dataformat,
            event_priority,
            isArray,
        )

        # 3. ASSERT
        df = myMsbClient.events[event_id].df
        dataFormat = myMsbClient.events[event_id].dataFormat
        self.assertEqual(MsbClient.validateValueForDataFormat(event_value, df, dataFormat, isArray), True)

    def test_validateValueSimpleStringArray_INVALID(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_dataformat = str
        event_value = ["Hello", 12, "!"]
        event_priority = 1
        isArray = True

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            event_dataformat,
            event_priority,
            isArray,
        )

        # 3. ASSERT
        df = myMsbClient.events[event_id].df
        dataFormat = myMsbClient.events[event_id].dataFormat
        self.assertEqual(MsbClient.validateValueForDataFormat(event_value, df, dataFormat, isArray), False)

    def test_validateValueSimpleIntegerArray(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_dataformat = DataType.INT32
        event_value = [1, 3, 56]
        event_priority = 1
        isArray = True

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            event_dataformat,
            event_priority,
            isArray,
        )

        # 3. ASSERT
        df = myMsbClient.events[event_id].df
        dataFormat = myMsbClient.events[event_id].dataFormat
        self.assertEqual(MsbClient.validateValueForDataFormat(event_value, df, dataFormat, isArray), True)

    def test_validateValueSimpleIntegerArray_INVALID(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_dataformat = int
        event_value = [1, True, 56]
        event_priority = 1
        isArray = True

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            event_dataformat,
            event_priority,
            isArray,
        )

        # 3. ASSERT
        df = myMsbClient.events[event_id].df
        dataFormat = myMsbClient.events[event_id].dataFormat
        self.assertEqual(MsbClient.validateValueForDataFormat(event_value, df, dataFormat, isArray), False)

    def test_validateValueSimpleNumberArray(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_dataformat = DataType.FLOAT
        event_value = [55.3, 1.2, 3.3]
        event_priority = 1
        isArray = True

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            event_dataformat,
            event_priority,
            isArray,
        )

        # 3. ASSERT
        df = myMsbClient.events[event_id].df
        dataFormat = myMsbClient.events[event_id].dataFormat
        self.assertEqual(MsbClient.validateValueForDataFormat(event_value, df, dataFormat, isArray), True)

    def test_validateValueSimpleNumberArray_INVALID(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_dataformat = DataType.FLOAT
        event_value = [55.3, 12, 3.3]
        event_priority = 1
        isArray = True

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            event_dataformat,
            event_priority,
            isArray,
        )

        # 3. ASSERT
        df = myMsbClient.events[event_id].df
        dataFormat = myMsbClient.events[event_id].dataFormat
        self.assertEqual(MsbClient.validateValueForDataFormat(event_value, df, dataFormat, isArray), False)

    def test_validateValueSelfDefinedComplexObject(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_priority = 1
        isArray = False

        complexObject_name_1 = "ComplexObject1"
        complexObject_property_name_1 = "megaprop"
        complexObject_isArray_1 = False
        complexObject_name_2 = "ComplexObject2"
        complexObject_property_name_2 = "superprop"
        complexObject_datatype_2 = "int32"
        complexObject_isArray_2 = True

        complexObject_1 = ComplexDataFormat(complexObject_name_1)
        complexObject_2 = ComplexDataFormat(complexObject_name_2)
        complexObject_2.addProperty(
            complexObject_property_name_2,
            complexObject_datatype_2,
            complexObject_isArray_2
        )
        complexObject_1.addProperty(
            complexObject_property_name_1,
            complexObject_2,
            complexObject_isArray_1
        )

        co1_value = {}
        co2_value = {}
        co2_value['superprop'] = [1, 3, 2]
        co1_value['megaprop'] = co2_value

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            complexObject_1,
            event_priority,
            isArray,
        )

        # 3. ASSERT
        df = myMsbClient.events[event_id].df
        dataFormat = myMsbClient.events[event_id].dataFormat
        self.assertEqual(MsbClient.validateValueForDataFormat(co1_value, df, dataFormat, isArray), True)

    def test_validateValueSelfDefinedComplexObject_INVALID(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_priority = 1
        isArray = False

        complexObject_name_1 = "ComplexObject1"
        complexObject_property_name_1 = "megaprop"
        complexObject_isArray_1 = False
        complexObject_name_2 = "ComplexObject2"
        complexObject_property_name_2 = "superprop"
        complexObject_datatype_2 = "int32"
        complexObject_isArray_2 = True

        complexObject_1 = ComplexDataFormat(complexObject_name_1)
        complexObject_2 = ComplexDataFormat(complexObject_name_2)
        complexObject_2.addProperty(
            complexObject_property_name_2,
            complexObject_datatype_2,
            complexObject_isArray_2
        )
        complexObject_1.addProperty(
            complexObject_property_name_1,
            complexObject_2,
            complexObject_isArray_1
        )

        co1_value = {}
        co2_value = {}
        co2_value['superprop'] = [1, "3", 2]
        co1_value['megaprop'] = co2_value

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            complexObject_1,
            event_priority,
            isArray,
        )

        # 3. ASSERT
        df = myMsbClient.events[event_id].df
        dataFormat = myMsbClient.events[event_id].dataFormat
        self.assertEqual(MsbClient.validateValueForDataFormat(co1_value, df, dataFormat, isArray), False)

    def test_validateValueSelfDefinedComplexObjectArray(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_priority = 1
        isArray = True

        complexObject_name_1 = "ComplexObject1"
        complexObject_property_name_1 = "megaprop"
        complexObject_isArray_1 = True
        complexObject_name_2 = "ComplexObject2"
        complexObject_property_name_2 = "superprop"
        complexObject_datatype_2 = "int32"
        complexObject_isArray_2 = True

        complexObject_1 = ComplexDataFormat(complexObject_name_1)
        complexObject_2 = ComplexDataFormat(complexObject_name_2)
        complexObject_2.addProperty(
            complexObject_property_name_2,
            complexObject_datatype_2,
            complexObject_isArray_2
        )
        complexObject_1.addProperty(
            complexObject_property_name_1,
            complexObject_2,
            complexObject_isArray_1
        )

        co1_value = {}
        co2_value = {}
        co2_value['superprop'] = [1, 3, 2]
        co1_value['megaprop'] = [co2_value]

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            complexObject_1,
            event_priority,
            isArray,
        )

        # 3. ASSERT
        df = myMsbClient.events[event_id].df
        dataFormat = myMsbClient.events[event_id].dataFormat
        self.assertEqual(MsbClient.validateValueForDataFormat([co1_value], df, dataFormat, isArray), True)

    def test_validateValueSelfDefinedComplexObjectArray_INVALID(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_priority = 1
        isArray = True

        complexObject_name_1 = "ComplexObject1"
        complexObject_property_name_1 = "megaprop"
        complexObject_isArray_1 = True
        complexObject_name_2 = "ComplexObject2"
        complexObject_property_name_2 = "superprop"
        complexObject_datatype_2 = "int32"
        complexObject_isArray_2 = True

        complexObject_1 = ComplexDataFormat(complexObject_name_1)
        complexObject_2 = ComplexDataFormat(complexObject_name_2)
        complexObject_2.addProperty(
            complexObject_property_name_2,
            complexObject_datatype_2,
            complexObject_isArray_2
        )
        complexObject_1.addProperty(
            complexObject_property_name_1,
            complexObject_2,
            complexObject_isArray_1
        )

        co1_value = {}
        co2_value = {}
        co2_value['superprop'] = [1, 3, "!!!"]
        co1_value['megaprop'] = [co2_value]

        # 2. ACT
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            complexObject_1,
            event_priority,
            isArray,
        )

        # 3. ASSERT
        df = myMsbClient.events[event_id].df
        dataFormat = myMsbClient.events[event_id].dataFormat
        self.assertEqual(MsbClient.validateValueForDataFormat([co1_value], df, dataFormat, isArray), False)


class TestMSBClientEventCaching(unittest.TestCase):
    """
    Test the event cache
    """

    def test_cacheEventIfNotConnected(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()
        myMsbClient.disableEventCache(False)
        myMsbClient.setEventCacheSize(2000)

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_dataformat = "string"
        event_priority = 1
        isArray = False
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            event_dataformat,
            event_priority,
            isArray,
        )
        event_value = "Hello World!"
        event_cached = True
        event_correlationId = str(uuid.uuid4())[-6:]

        # 2. ACT
        myMsbClient.publish(
            event_id,
            event_value,
            event_priority,
            event_cached,
            None,
            event_correlationId,
        )

        # 3. ASSERT
        _event = None
        eventFoundInCache = False
        for e in myMsbClient.eventCache:
            _event = json.loads(e)
            if _event["eventId"] == event_id:
                eventFoundInCache = True
                # logging.debug(str(_event))
        self.assertEqual(eventFoundInCache, True)
        self.assertEqual(_event["dataObject"], event_value)
        self.assertEqual(_event["priority"], event_priority)
        self.assertEqual(_event["correlationId"], event_correlationId)

    def test_cacheEventIfNotConnectedByShiftingFullCache(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()
        myMsbClient.disableEventCache(False)
        myMsbClient.setEventCacheSize(1)

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_dataformat = "string"
        event_priority = 1
        isArray = False
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            event_dataformat,
            event_priority,
            isArray,
        )
        event_value_older = "Test!"
        event_value = "Hello World!"
        event_cached = True
        event_correlationId = str(uuid.uuid4())[-6:]

        # 2. ACT
        myMsbClient.publish(
            event_id,
            event_value,
            event_priority,
            event_cached,
            None,
            event_correlationId,
        )
        myMsbClient.publish(
            event_id,
            event_value_older,
            event_priority,
            event_cached,
            None,
            event_correlationId,
        )
        myMsbClient.publish(
            event_id,
            event_value,
            event_priority,
            event_cached,
            None,
            event_correlationId,
        )

        # 3. ASSERT
        _event = None
        eventFoundInCache = False
        for e in myMsbClient.eventCache:
            _event = json.loads(e)
            if _event["eventId"] == event_id:
                eventFoundInCache = True
                # logging.debug(str(_event))
        self.assertEqual(eventFoundInCache, True)
        self.assertEqual(_event["dataObject"], event_value)
        self.assertEqual(_event["priority"], event_priority)
        self.assertEqual(_event["correlationId"], event_correlationId)

    def test_doNotCacheEventIfGloballyDisabled(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()
        myMsbClient.disableEventCache(True)
        myMsbClient.setEventCacheSize(2000)

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_dataformat = "string"
        event_priority = 1
        isArray = False
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            event_dataformat,
            event_priority,
            isArray,
        )
        event_value = "Hello World!"
        event_cached = True
        event_correlationId = str(uuid.uuid4())[-6:]

        # 2. ACT
        myMsbClient.publish(
            event_id,
            event_value,
            event_priority,
            event_cached,
            None,
            event_correlationId,
        )

        # 3. ASSERT
        _event = None
        eventFoundInCache = False
        for e in myMsbClient.eventCache:
            _event = json.loads(e)
            if _event["eventId"] == event_id:
                eventFoundInCache = True
        self.assertEqual(eventFoundInCache, False)

    def test_doNotCacheEventIfDisabledForEvent(self):
        # 1. ARRANGE
        myMsbClient = MsbClient()
        myMsbClient.disableEventCache(False)
        myMsbClient.setEventCacheSize(2000)

        event_id = str(uuid.uuid4())[-6:]
        event_name = "EVENT " + event_id
        event_description = "EVENT Description " + event_id
        event_dataformat = "string"
        event_priority = 1
        isArray = False
        myMsbClient.addEvent(
            event_id,
            event_name,
            event_description,
            event_dataformat,
            event_priority,
            isArray,
        )
        event_value = "Hello World!"
        event_cached = False
        event_correlationId = str(uuid.uuid4())[-6:]

        # 2. ACT
        myMsbClient.publish(
            event_id,
            event_value,
            event_priority,
            event_cached,
            None,
            event_correlationId,
        )

        # 3. ASSERT
        _event = None
        eventFoundInCache = False
        for e in myMsbClient.eventCache:
            _event = json.loads(e)
            if _event["eventId"] == event_id:
                eventFoundInCache = True
        self.assertEqual(eventFoundInCache, False)

# define a sample function which will be passed to the function description


def printMsg(msg):
    print(str(msg))


class myClass():
    def myNonStaticPrintMethod(self, msg):
        print(str(msg))
