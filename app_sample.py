# -*- coding: utf-8 -*-
"""
Copyright (c) 2019 Fraunhofer Institute for Manufacturing Engineering and Automation (IPA)
Authors: Daniel Stock, Matthias Stoehr

Licensed under the Apache License, Version 2.0
See the file "LICENSE" for the full license governing this code.
"""
import datetime
import threading
import uuid

from msb_client.ComplexDataFormat import ComplexDataFormat
from msb_client.DataType import DataType
from msb_client.Event import Event
from msb_client.Function import Function
from msb_client.MsbClient import MsbClient

if __name__ == "__main__":
    """This is a sample client for the MSB python client library."""
    # define service properties as constructor parameters
    SERVICE_TYPE = "SmartObject"
    SO_UUID = str(uuid.uuid1())
    SO_NAME = "MSBClientPythonAppSample" + SO_UUID[-6:]
    SO_DESCRIPTION = "MSBClientPythonAppSample description"  
    SO_TOKEN = SO_UUID[-6:]
    myMsbClient = MsbClient(
        SERVICE_TYPE,
        SO_UUID,
        SO_NAME,
        SO_DESCRIPTION,
        SO_TOKEN,
    )
    # otherwise the application.properties file will be read
    # myMsbClient = MsbClient()

    # msb_url = 'wss://localhost:8084'
    # msb_url = 'ws://localhost:8085'
    msb_url = 'ws://ws2.msb.edu.virtualfortknox.de'

    # enable debug log messages (default = disabled).
    myMsbClient.enableDebug(True)

    # enable ws lib trace console output (default = disabled).
    myMsbClient.enableTrace(False)

    # enable data format and message data validation (default = enabled).
    # might impact performance
    myMsbClient.enableDataFormatValidation(True)

    # enable auto reconnect for the client (default = enabled).
    myMsbClient.disableAutoReconnect(False)

    # set the reconnect interval time in ms (default = 10000 ms).
    myMsbClient.setReconnectInterval(10000)

    # enable or disable the message buffer, 
    # which will buffer sent event messages when no active connection is available (default = enabled).
    myMsbClient.disableEventCache(False)

    # set event cache size (default = 1000 message events).
    myMsbClient.setEventCacheSize(1000)

    # disable SSL hostname check and certificate validation for self signed certificates (default = enabled).
    myMsbClient.disableHostnameVerification(True)  

    # add a configuration parameter to the self description.
    # configuration parameters are published to the MSB and can be changed from the MSB GUI in real time
    # (key, value, datatype)
    myMsbClient.addConfigParameter("testParam1", 17, DataType.INT32)
    myMsbClient.addConfigParameter("testParam2", "Hello World!", DataType.STRING)
    myMsbClient.addConfigParameter("testParam3", 3.3, DataType.FLOAT)
    myMsbClient.addConfigParameter("testParam4", True, DataType.BOOLEAN)

    # to retrieve a configuration parameter, you can retrieve it as follows:
    # myMsbClient.getConfigParameter('testParam1')
    # e.g.
    def printParameter():
        print(str(myMsbClient.getConfigParameter("testParam1")))

    # change a configuration parameter locally:
    # myMsbClient.changeConfigParameter('testParam1', 17)

    # create new event object
    # parameter 1 (str:‘EVENT1’): internal event name reference (inside program code)
    # parameter 2 (str:‘Event1’): MSB event name (visible in MSB GUI)
    # parameter 3 (str:'Event1_description’): description which shows up in MSB GUI
    # parameter 4 (DataType:DataType.STRING): type of event payload
    # parameter 5 (int:1): event priority – value range: [0, 1, 2] (low, medium, high)
    # parameter 6 (bool:optional): True if payload is an array of parameter 4
    event1 = Event("EVENT1", "Event1", "Event1_description", DataType.STRING, 1)

    # optionally define the data format as an array
    event2 = Event("EVENT2", "Event2", "Event2_description", DataType.INT32, 0, True)

    # if the event doesn't have a payload, just pass None as the data type parameter
    event3 = Event("EVENT3", "Event3", "Event3_description", None, 0)

    # event to demonstrate reponse events
    response_event1 = Event(
        "RESPONSE_EVENT1",
        "Response Event1",
        "ResponseEvent1_description",
        DataType.STRING,
        1,
    )

    # the final data format can be provided as a valid JSON string, the array function parameter will be ignored.
    manual_event = Event(
        "MANUAL_EVENT",
        "Manual event",
        "Manual event description",
        '{ "type": "number",  "format": "double" }',
        0,
        True,
    )

    # the final data format can be provided as a valid JSON object
    complex_json_event = Event(
        "COMPLEX_JSON_EVENT",
        "Manual event",
        "Manual event description",
        {
            "Member" : {
                "type" : "object",
                "properties" : {
                    "name" : {
                        "type" : "string"
                    },
                    "status" : {
                        "enum" : [ "present", "absent" ],
                        "type" : "string"
                    }
                }
            },
            "Team" : {
                "type" : "object",
                "properties" : {
                    "staff" : {
                        "type" : "array",
                        "items" : {
                            "$ref" : "#/definitions/Member"
                        }
                    }
                }
            },
            "dataObject" : {
                "$ref" : "#/definitions/Team"
            }
        },
        0,
        False,
    )

    # add event objects to MSB client
    myMsbClient.addEvent(event1)
    myMsbClient.addEvent(event2)
    myMsbClient.addEvent(event3)
    myMsbClient.addEvent(response_event1)
    myMsbClient.addEvent(manual_event)
    myMsbClient.addEvent(complex_json_event)

    # optionally, add an event directly in line
    myMsbClient.addEvent(
        "EVENT4", "Event4", "Event4_description", DataType.INT32, 0, False
    )

    myMsbClient.addEvent(
        "DATEEVENT", "DateEvent", "DateEvent_description", DataType.DATETIME, 0, False
    )

    # define a complex data format to be used in an event
    # init the complex data format
    myDevice = ComplexDataFormat("MyDevice")
    myModule = ComplexDataFormat("MyModule")

    # add the properties to the complex objects
    # (property_name, property_datatype, isArray)
    myModule.addProperty("moduleName", DataType.STRING, False)
    myDevice.addProperty("deviceName", DataType.STRING, False)
    myDevice.addProperty("deviceWeight", DataType.FLOAT, False)
    myDevice.addProperty("submodules", myModule, True)

    # add the event with the complex data format
    myMsbClient.addEvent(
        "EVENT5", "Event5", "Event5_description", myDevice, 0, False
    )

    # define the function which will be passed to the function description
    def printMsg(msg):
        print(str(msg["dataObject"]))

    # define the function which will be passed to the function description
    # this example shows
    # When a function call is calling a function which has a response event,
    # you have to pass the "correlationId" parameter which is provided by the function callback
    # to the client's publish function. If you pass "None", nothing will be attached.
    def sendResponseEventExample(msg):
        print(str(msg))
        # don't forget to pass the parameter name for the correlationId if you're not passing all parameters
        myMsbClient.publish(
            "RESPONSE_EVENT1", msg["dataObject"], correlationId=msg["correlationId"]
        )

    # create new function object
    # This example has no response events.
    # parameter 1 (str:‘FUNCTION1’): internal function name reference (inside program code)
    # parameter 2 (str:‘Function1’): MSB function name (visible in MSB GUI)
    # parameter 3 (str:'Function1_description’): description which shows up in MSB GUI
    # parameter 4 (DataType:DataType.STRING): type of data the function will handle
    # parameter 5 (fnPointer:printMsg): pointer to the function implementation
    # parameter 6 (bool:optional): True if payload is an array of parameter 4
    # parameter 7 (list:optional): array of response events e.g. ['RESPONSE_EVENT1']
    function1 = Function(
        "FUNCTION1", "Function1", "Function1_description", DataType.STRING, printMsg, True, []
    )
    # add function objects to MSB client
    myMsbClient.addFunction(function1)

    # optionally, add function directly in line
    # this example has one response event.
    myMsbClient.addFunction(
        "FUNCTION2",
        "Function2",
        "Function2_description",
        DataType.STRING,
        sendResponseEventExample,
        False,
        ["RESPONSE_EVENT1"],
    )

    # define a function with a complex data format
    f3 = Function(
        "FUNCTION3",
        "Function3",
        "Function3_description",
        myDevice,
        printMsg,
        False,
    )
    myMsbClient.addFunction(f3)

    # if the function is not requiring any parameters None can be passed for the data format
    # This example has multiple response events.
    myMsbClient.addFunction(
        "PRINT_PARAMETER",
        "Print parameter",
        "Print parameter",
        None,
        printParameter,
        False,
        ["EVENT1", "EVENT2"],
    )

    # the final data format can be provided as a valid JSON object
    myMsbClient.addFunction(
        "COMPLEX_JSON_FUNCTION",
        "Function JSON based",
        "Description function JSON based",
        {
            "Member" : {
                "type" : "object",
                "properties" : {
                    "name" : {
                        "type" : "string"
                    },
                    "status" : {
                        "enum" : [ "present", "absent" ],
                        "type" : "string"
                    }
                }
            },
            "Team" : {
                "type" : "object",
                "properties" : {
                    "staff" : {
                        "type" : "array",
                        "items" : {
                            "$ref" : "#/definitions/Member"
                        }
                    }
                }
            },
            "dataObject" : {
                "$ref" : "#/definitions/Team"
            }
        },
        printMsg,
        False,
        ["EVENT1", "EVENT2"],
    )

    # helper function which will repeat the passed function in the defined interval in seconds,
    # this example doesn't check for race condition
    def set_interval(func, sec):
        def func_wrapper():
            set_interval(func, sec)
            func()

        t = threading.Timer(sec, func_wrapper)
        t.start()
        return t

    def send_data():
        # myMsbClient.publish("EVENT1", "Hello World!")

        # myMsbClient.publish('EVENT2', [1,2,4,5])

        # myMsbClient.publish('DATEEVENT', datetime.datetime.now())

        # pepare the complex ovbject based on a complex data format
        # use it as event value
        myModuleObj = {}
        myModuleObj['moduleName'] = 'Module 1'
        myDeviceObj = {}
        myDeviceObj['deviceName'] = 'Device 1'
        myDeviceObj['deviceWeight'] = 1.3
        myDeviceObj['submodules'] = [myModuleObj]
        myMsbClient.publish('EVENT5', myDeviceObj)

    # print the generated self description for debug purposes. This function has to be called after all events,
    # functions and parameters have been added or else the output will be incomplete.
    print(myMsbClient.objectToJson(myMsbClient.getSelfDescription()))

    # connect by defining a broker url in line
    # myMsbClient.connect('wss://localhost:8084')

    # connect to server by defining server url in line, otherwise the application.properties file will be read
    myMsbClient.connect(msb_url)
    # myMsbClient.connect()

    # register client on MSB
    myMsbClient.register()

    # disconnect client from MSB
    # myMsbClient.disconnect()

    # call send_data() function every 5 seconds
    # be aware of racing conditions which might be created here
    set_interval(send_data, 5)
