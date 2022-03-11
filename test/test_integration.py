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
import os
import re
import logging
import uuid
import time
import json
import requests

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


# Check env variables
customIp = None
if "TESTENV_CUSTOMIP" in os.environ:
    customIp = os.environ["TESTENV_CUSTOMIP"]
    customIp = customIp.rstrip("\n")
    logging.info("Custom IP was set >" + str(customIp) + "<")

# Main constants
OWNER_UUID = "7c328ad1-cea5-410e-8dd8-6c7ca5a2e4f5"
SO_UUID = str(uuid.uuid1())
SO_NAME = "MSBClientIntegrationTestSO" + SO_UUID[-6:]
SO_DESCRIPTION = "MSBClientIntegrationTestSO description"
FLOW_NAME = "MSBClientIntegrationTestFlow" + SO_UUID[-6:]
TIMEOUT = 30.0
WAITING_TIME = 5
CORRELATIOON_ID_FOR_TEST_SIMPLE_ARRAY = "123456789987654321"
CORRELATIOON_ID_FOR_TEST_COMPLEX_OBJECT = "349857439587349587"

soCreated = False
flow_id = 0
flowCreated = False
flowDeployed = False
receivedArrayEv = False
receivedComplexEv = False

owner_uuid = OWNER_UUID

# Rest urls
broker_url = "https://localhost:8084"
so_url = "http://localhost:8081"
flow_url = "http://localhost:8082"

# replace hostname with customIp
if customIp:
    broker_url = re.sub(
        r":\/\/(www[0-9]?\.)?(.[^/:]+)", "://" + str(customIp), broker_url
    )
    so_url = re.sub(r":\/\/(www[0-9]?\.)?(.[^/:]+)", "://" + str(customIp), so_url)
    flow_url = re.sub(r":\/\/(www[0-9]?\.)?(.[^/:]+)", "://" + str(customIp), flow_url)
# replace broker url with env
if "TESTENV_BROKER_URL" in os.environ:
    broker_url = os.environ["TESTENV_BROKER_URL"]
    broker_url = broker_url.rstrip("\n")
    logging.info("Broker Url Env was set >" + str(broker_url) + "<")
if "TESTENV_SO_URL" in os.environ:
    so_url = os.environ["TESTENV_SO_URL"]
    so_url = so_url.rstrip("\n")
    logging.info("SO Url Env was set >" + str(so_url) + "<")
if "TESTENV_FLOW_URL" in os.environ:
    flow_url = os.environ["TESTENV_FLOW_URL"]
    flow_url = flow_url.rstrip("\n")
    logging.info("Flow Url Env was set >" + str(flow_url) + "<")
if "TESTENV_OWNER_UUID" in os.environ:
    owner_uuid = os.environ["TESTENV_OWNER_UUID"]
    owner_uuid = owner_uuid.rstrip("\n")
    logging.info("Owner Uuid Env was set >" + str(owner_uuid) + "<")

myMsbClient = None
flow_json = None


class IntegrationTestMSBClientRestInterfaces(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_smartobjectmanagement_availability(self):
        logging.info("Smart Object URL: >" + so_url + "<")

        response = requests.get(
            so_url + "/service/token/" + owner_uuid, verify=False
        )
        self.assertEqual(response.status_code, 201, "Can not reach smart-object-management")

    @pytest.mark.run(order=2)
    def test_integrationflowmanagement_availability(self):
        logging.info("Flow URL: >" + str(flow_url) + "<")

        response = requests.get(
            flow_url + "/integrationFlow/customer/" + owner_uuid, verify=False
        )
        self.assertEqual(response.status_code, 200, "Can not reach integration-flow-management")


class IntegrationTestMSBClientBasicCommunication(unittest.TestCase):

    @pytest.mark.run(order=3)
    def test_getVerificationToken(self):

        logging.info("Broker URL: >" + str(broker_url) + "<")

        # get valid verification token
        response = requests.get(
            so_url + "/service/token/" + owner_uuid, verify=False
        )
        self.assertEqual(
            response.status_code,
            201,
            "Can not get verification token from smart-object-management",
        )
        response_dict = json.loads(response.text)
        self.assertTrue(
            "token" in response_dict, "Response doesn't contain token key"
        )
        verification_token = response_dict["token"]
        self.assertNotEqual(
            str(verification_token),
            "undefined",
            "Response contain token key, but is undefined",
        )
        logging.info(
            "Generated verification token: >" + str(verification_token) + "<"
        )

        # setup msb client
        setup_msbclient(verification_token)
        # print smart object as json
        logging.debug("Self Description" + myMsbClient.objectToJson(myMsbClient.getSelfDescription()))

    @pytest.mark.run(order=4)
    def test_communication(self):

        try:

            #
            # Test add event to cache
            #
            # send test data
            myMsbClient.publish(
                "SIMPLE_EVENT1_STRING",
                "Simple String",
                None,
                True,  # cached
                datetime.datetime.utcnow(),
                None,
            )
            eventFoundInCache = False
            for e in myMsbClient.eventCache:
                _event = json.loads(e)
                if _event["eventId"] == "SIMPLE_EVENT1_STRING":
                    eventFoundInCache = True
                    logging.debug("Event in cache: " + str(_event))
            self.assertEqual(eventFoundInCache, True)

            #
            # Test connect Client
            #
            # start msb client
            myMsbClient.connect(broker_url)
            # wait for IO_CONNECTED
            timeout = time.time() + 60
            while True:
                if myMsbClient.connected:
                    logging.info("IO_CONNECTED message detected")
                    break
                if time.time() > timeout:
                    self.assertTrue(
                        myMsbClient.connected,
                        "Could not detect an IO_CONNECTED message within an acceptable timeframe",
                    )
                    break
                time.sleep(WAITING_TIME)

            #
            # Test register Client
            #
            # register client on MSB
            myMsbClient.register()
            # wait for IO_REGISTERED
            timeout = time.time() + 60 * 2
            while True:
                if myMsbClient.registered:
                    logging.info("IO_REGISTERED message detected")
                    break
                if time.time() > timeout:
                    self.assertTrue(
                        myMsbClient.registered,
                        "Could not detect an IO_REGISTERED message within an acceptable timeframe",
                    )
                    break
                time.sleep(WAITING_TIME)
            global soCreated
            soCreated = True

            #
            # Test cached events get published now
            #
            # check event cache size to be empty
            time.sleep(WAITING_TIME)
            self.assertEqual(len(myMsbClient.eventCache), 0)

            #
            # Test change configuration parameter
            #
            myMsbClient.changeConfigParameter("testParam1", False)
            self.assertEqual(myMsbClient.getConfigParameter("testParam1"), False)

            #
            # Test create integration flow
            #
            # setup flow
            setup_flow()
            logging.debug(flow_json)

            # create flow
            response = requests.post(
                flow_url + "/integrationFlow/create",
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                data=str(flow_json),
                verify=False
            )
            response_dict = json.loads(response.text)
            self.assertEqual(
                response.status_code, 201, str("Creating integration flow failed: " + str(response))
            )
            logging.debug(response_dict)
            global flowCreated
            flowCreated = True

            global flow_id
            self.assertTrue("id" in response_dict, "Response doesn't contain id key")
            flow_id = response_dict["id"]
            logging.info("Flow id: %d" % flow_id)

            time.sleep(WAITING_TIME)

            #
            # Test deploy integration flow
            #
            # deploy flow
            response = requests.put(
                flow_url + "/integrationFlow/" + str(flow_id) + "/deploy",
                verify=False
            )
            self.assertEqual(
                response.status_code, 200, str("Deploying integration flow failed: " + str(response))
            )
            global flowDeployed
            flowDeployed = True

            time.sleep(WAITING_TIME)

            #
            # Test publish and receive data (simple array)
            #
            # send test data
            myMsbClient.publish(
                "arrayev",
                ["Hello", "World", "!"],
                None,
                True,
                None,
                CORRELATIOON_ID_FOR_TEST_SIMPLE_ARRAY,
            )

            # wait for function /arrayfun called by event arrayev
            timeout = time.time() + 60
            while True:
                if receivedArrayEv:
                    logging.info("Function /arrayfun called")
                    self.assertTrue(
                        receivedArrayEvIndexCheck, "Wrong message received in /arrayfun"
                    )
                    self.assertTrue(
                        receivedArrayEvWithCorrectCorrelationId,
                        "Function /arrayfun not called within an acceptable timeframe",
                    )
                    break
                if time.time() > timeout:
                    self.assertTrue(receivedArrayEv, "Invalid or missing correlationId")
                    break
                time.sleep(WAITING_TIME)

            time.sleep(WAITING_TIME)

            #
            # Test publish and receive data (complex object)
            #
            # send test data
            myMsbClient.publish(
                "COMPLEX_JSON_EVENT",
                {"staff": [{"name": "Max Mustermann", "status": "present"},
                           {"name": "Mia Musterfrau", "status": "absent"}]},
                None,
                True,
                None,
                CORRELATIOON_ID_FOR_TEST_COMPLEX_OBJECT,
            )

            # wait for function COMPLEX_JSON_FUNCTION called by event COMPLEX_JSON_EVENT
            timeout = time.time() + 60
            while True:
                if receivedComplexEv:
                    logging.info("Function COMPLEX_JSON_FUNCTION called")
                    self.assertTrue(
                        receivedComplexEvCheck, "Wrong message received in COMPLEX_JSON_FUNCTION"
                    )
                    self.assertTrue(
                        receivedComplexEvWithCorrectCorrelationId,
                        "Function COMPLEX_JSON_FUNCTION not called within an acceptable timeframe",
                    )
                    break
                if time.time() > timeout:
                    self.assertTrue(receivedComplexEv, "Invalid or missing correlationId")
                    break
                time.sleep(WAITING_TIME)

        except AssertionError:
            raise
        finally:

            #
            # Test undeploy integration flow
            #
            # undeploy flow
            if flowDeployed:
                response = requests.put(
                    flow_url + "/integrationFlow/" + str(flow_id) + "/undeploy",
                    verify=False
                )
                self.assertEqual(
                    response.status_code,
                    200,
                    str("Undeploying integration flow failed: " + str(response)),
                )

                time.sleep(WAITING_TIME)

            #
            # Test delete integration flow
            #
            # delete flow
            if flowCreated:
                response = requests.delete(
                    flow_url + "/integrationFlow/" + str(flow_id),
                    headers={
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                    },
                    verify=False
                )
                self.assertEqual(
                    response.status_code, 200, str("Deleting integration flow failed")
                )

                time.sleep(WAITING_TIME)

            #
            # Test delete smart object
            #
            # delete smart object
            if soCreated:
                response = requests.delete(
                    so_url + "/smartobject/" + SO_UUID,
                    headers={"Content-Type": "application/json"},
                    verify=False
                )
                self.assertEqual(response.status_code, 200, "Problem deleting smart object")

                time.sleep(WAITING_TIME)


def setup_flow():
    global flow_json
    with open("test/integration_flow.json") as f:
        flow_json = f.read()

    assert len(flow_json) > 0, "Failed to read file"

    flow_json = flow_json.replace("%%%%FLOWNAME%%%%", FLOW_NAME)
    flow_json = flow_json.replace("%%%%OWNERUUID%%%%", owner_uuid)
    flow_json = flow_json.replace("%%%%SOUUID1%%%%", SO_UUID)
    flow_json = flow_json.replace("%%%%SOUUID2%%%%", SO_UUID)
    flow_json = flow_json.replace("%%%%SONAME1%%%%", SO_NAME)
    flow_json = flow_json.replace("%%%%SONAME2%%%%", SO_NAME)
    flow_json = flow_json.replace("\n", "")

    assert "%%%%" not in flow_json, "String replacement went wrong"


def setup_msbclient(verification_token):

    logging.debug("Setup MSB Client")

    # Init msb client
    global myMsbClient
    myMsbClient = MsbClient(
        "SmartObject", SO_UUID, SO_NAME, SO_DESCRIPTION, verification_token
    )
    myMsbClient.enableDebug(True)
    myMsbClient.enableTrace(False)
    myMsbClient.enableDataFormatValidation(True)
    myMsbClient.disableEventCache(False)
    myMsbClient.setEventCacheSize(1000)
    myMsbClient.disableAutoReconnect(False)
    myMsbClient.setReconnectInterval(10000)
    myMsbClient.disableHostnameVerification(True)
    myMsbClient.enableThreadAsDaemon(True)

    # add a configuration parameter to the self description
    config_param_name_1 = "testParam1"
    config_param_value_1 = True
    config_param_datatype_1 = bool

    config_param_name_2 = "testParam2"
    config_param_value_2 = "StringValue"
    config_param_datatype_2 = str

    config_param_name_3 = "testParam3"
    config_param_value_3 = 1000
    config_param_datatype_3 = "int32"

    config_param_name_4 = "testParam3_2"
    config_param_value_4 = 2000
    config_param_datatype_4 = int

    config_param_name_5 = "testParam5"
    config_param_value_5 = 3.3
    config_param_datatype_5 = float

    config_param_name_6 = "testParam6"
    config_param_value_6 = 3.3
    config_param_datatype_6 = "float"

    config_param_name_7 = "testParam7"
    config_param_value_7 = datetime.datetime.now()
    config_param_datatype_7 = "date-time"

    myMsbClient.addConfigParameter(config_param_name_1, config_param_value_1, config_param_datatype_1)
    myMsbClient.addConfigParameter(config_param_name_2, config_param_value_2, config_param_datatype_2)
    myMsbClient.addConfigParameter(config_param_name_3, config_param_value_3, config_param_datatype_3)
    myMsbClient.addConfigParameter(config_param_name_4, config_param_value_4, config_param_datatype_4)
    myMsbClient.addConfigParameter(config_param_name_5, config_param_value_5, config_param_datatype_5)
    myMsbClient.addConfigParameter(config_param_name_6, config_param_value_6, config_param_datatype_6)
    myMsbClient.addConfigParameter(config_param_name_7, config_param_value_7, config_param_datatype_7)

    logging.debug("Self Description - added config params")
    # add events to the client: as single param
    myMsbClient.addEvent(
        "SIMPLE_EVENT1_STRING",
        "Simple event 1",
        "Simple event with string",
        DataType.STRING,
        "LOW",
        False,
    )
    myMsbClient.addEvent(
        "SIMPLE_EVENT2_INTEGER_ARRAY",
        "Simple event 2",
        "Simple event with integer array",
        DataType.INT32,
        0,
        True
    )
    myMsbClient.addEvent(
        "SIMPLE_EVENT3_JSONDATAFORMAT",
        "Simple event 3",
        "Simple event with JSON stringified dataformat",
        '{ "type": "number",  "format": "float" }',
        2,
        False
    )
    myMsbClient.addEvent(
        "SIMPLE_EVENT4_NOPAYLOAD",
        "Simple event 4",
        "Simple event with no payload",
        None,
        0,
        False
    )
    myMsbClient.addEvent(
        "DATE_EVENT",
        "Date Event",
        "Simple event with datetime",
        DataType.DATETIME,
        0,
        False
    )
    myMsbClient.addEvent(
        "arrayev",
        "Array Event",
        "Array Event for testing",
        DataType.STRING,
        "LOW",
        True
    )

    # add events to the client: as event object
    event1 = Event(
        "EVENT1",
        "Event 1",
        "Event with string",
        DataType.STRING,
        "LOW",
        False
    )
    myMsbClient.addEvent(event1)
    event1 = Event(
        "EVENT2",
        "Event 2",
        "Event with number",
        DataType.FLOAT,
        "LOW",
        False
    )
    myMsbClient.addEvent(event1)

    logging.debug("Self Description - added simple events")

    # define properties for complex data format to be used in an event
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
    # initialize the complex data format
    complexObject_1 = ComplexDataFormat(complexObject_name_1)
    complexObject_2 = ComplexDataFormat(complexObject_name_2)
    complexObject_3 = ComplexDataFormat(complexObject_name_3)
    complexObject_4 = ComplexDataFormat(complexObject_name_4)
    # add properties to the nested complex data formats
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
    # add the event with the complex data format
    myMsbClient.addEvent(
        "EVENT3_COMPLEX",
        "Event 3 Complex Data Format",
        "Event wit a 4-level complex data format",
        complexObject_1,
        0,
        True,
    )

    # the final data format can be provided as a valid JSON object
    myMsbClient.addEvent(
        "COMPLEX_JSON_EVENT",
        "JSON based event",
        "JSON based event description",
        {
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
        },
        0,
        False,
    )

    logging.debug("Self Description - added complex events")

    # define the function which will be passed to the function description
    def printMsg(msg):
        print(str(msg["dataObject"]))

    # add functions to the client: as single param
    myMsbClient.addFunction(
        "FUNCTION1",
        "Function 1",
        "Description function 1",
        "int32",
        printMsg,
        False,
        ["EVENT1", "EVENT2"],
    )

    # add functions to the client: as function object
    function2 = Function(
        "FUNCTION2",
        "Function 2",
        "Description function 2",
        str,
        printMsg,
        False,
        ["EVENT1", "EVENT2"],
    )
    myMsbClient.addFunction(function2)

    # the final data format can be provided as a valid JSON object
    myMsbClient.addFunction(
        "COMPLEX_JSON_FUNCTION",
        "Function JSON based",
        "Description function JSON based",
        {
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
        },
        complexfun_implementation,
        False,
        ["EVENT1", "EVENT2"],
    )

    # myInstance = myClass()

    # add the function to be tested in integration flow
    function_arrayfun = Function(
        "/arrayfun",
        "Array Function",
        "Array Function for testing",
        str,
        arrayfun_implementation,
        # myInstance.myNonStatic_arrayfun_implementation,
        True,
        None,
    )
    myMsbClient.addFunction(function_arrayfun)

    logging.debug("Self Description - added functions")

# define the function which will be passed to the function description


def arrayfun_implementation(msg):
    logging.debug("Array Function has been called, message: " + str(msg["a"]))
    global receivedArrayEv
    global receivedArrayEvIndexCheck
    global receivedArrayEvWithCorrectCorrelationId
    receivedArrayEvIndexCheck = True
    receivedArrayEvIndexCheck = str(msg["a"][0]) == "Hello"
    receivedArrayEvIndexCheck = str(msg["a"][1]) == "World"
    receivedArrayEvIndexCheck = str(msg["a"][2]) == "!"
    logging.debug(
        "Array Function has been called, correlationId: " + msg["correlationId"]
    )
    receivedArrayEvWithCorrectCorrelationId = (
        str(msg["correlationId"]) == CORRELATIOON_ID_FOR_TEST_SIMPLE_ARRAY
    )
    receivedArrayEv = True


def complexfun_implementation(msg):
    logging.debug("Complex Function has been called, message: " + str(msg["dataObject"]))
    global receivedComplexEv
    global receivedComplexEvCheck
    global receivedComplexEvWithCorrectCorrelationId

    receivedComplexEvCheck = True
    receivedComplexEvCheck = \
        str(msg["dataObject"]) == \
        str(
            {"staff": [
                {"name": "Max Mustermann", "status": "present"},
                {"name": "Mia Musterfrau", "status": "absent"}
            ]}
        )
    logging.debug(
        "Complex Function has been called, correlationId: " + msg["correlationId"]
    )
    receivedComplexEvWithCorrectCorrelationId = (
        str(msg["correlationId"]) == CORRELATIOON_ID_FOR_TEST_COMPLEX_OBJECT
    )
    receivedComplexEv = True


class myClass():
    def myNonStatic_arrayfun_implementation(self, msg):
        arrayfun_implementation(msg)
