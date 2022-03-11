# -*- coding: utf-8 -*-
"""
Copyright (c) 2019 Fraunhofer Institute for Manufacturing Engineering and Automation (IPA)
Authors: Daniel Stock, Matthias Stoehr

Licensed under the Apache License, Version 2.0
See the file "LICENSE" for the full license governing this code.
"""

import websocket, threading, json, jsonschema, ssl, time, uuid, os, logging
from random import randint
import datetime
import copy

from .Event import Event
from .ComplexDataFormat import ComplexDataFormat
from .Function import Function
from .DataFormat import getDataType


class MsbClient(websocket.WebSocketApp):
    """Definition of the msb client to handle the creation of the self-description
     and communication with the msb websocket interface.
    """

    def __init__(
        self,
        service_type=None,
        uuid=None,
        name=None,
        description=None,
        token=None,
        applicationPropertiesCustomPath=None
    ):
        """Initializes a new msb client.

        If no parameters are provided an application.properties file with the main configuration needs to be present.
        Otherwise the config data can be provided as constructor parameters

        Args:
            service_type (str): The service type of the service ('Application' or 'SmartObject')
            uuid (str): The uuid of the service as valid V4 UUID
            name (str): The name of the service
            description (str): The description of the service
            token (str): The token of the service used to verify service via MSB GUI or Rest
        Returns:
            MsbClient: The msb client object to specify the service and handle MSB connection
        """

        self.msb_url = ""
        self.msb_url_with_wspath = ""
        self.applicationPropertiesCustomPath = applicationPropertiesCustomPath

        # debugging
        self.debug = False
        self.trace = False
        self.dataFormatValidation = True

        # connection params
        self.connected = False
        self.registered = False
        self.autoReconnect = True
        self.reconnecting = False
        self.userDisconnect = False
        self.reconnectInterval = 10

        # client-side heartbeats
        self.keepAlive = False
        self.heartbeat_interval = 8

        # sockJs framing
        self.sockJsFraming = True

        # event caching
        self.eventCache = []
        self.eventCacheEnabled = True
        self.eventCacheSize = 1000
        self.maxMessageSize = 1000000

        # smart object definition
        self.functions = {}
        self.events = {}
        self.configuration = {}
        self.configuration["parameters"] = {}

        # // socket
        self.ws = None
        self.hostnameVerification = False
        self.threadAsDaemonEnabled = False

        # check if all params are present or if the application.properties file will be used
        if (service_type or uuid or name or description or token) is not None:
            self.service_type = service_type
            self.uuid = uuid
            self.name = name
            self.description = description
            self.token = token
        else:
            self.readConfig()

    # list of all valid MSB message types
    MSBMessageTypes = [
        "IO",
        "NIO",
        "IO_CONNECTED",
        "IO_REGISTERED",
        "IO_PUBLISHED",
        "NIO_ALREADY_CONNECTED",
        "NIO_REGISTRATION_ERROR",
        "NIO_UNEXPECTED_REGISTRATION_ERROR",
        "NIO_UNAUTHORIZED_CONNECTION",
        "NIO_EVENT_FORWARDING_ERROR",
        "NIO_UNEXPECTED_EVENT_FORWARDING_ERROR",
        "ping"
    ]

    def sendBuf(self):
        for idx, msg in enumerate(self.eventCache):
            try:
                if self.connected and self.registered:
                    logging.debug("SENDING (BUF): " + msg)
                    if self.sockJsFraming:
                        _msg = self.objectToJson(msg).replace("\\n", "")
                        self.ws.send('["E ' + _msg[1:-1] + '"]')
                    else:
                        self.ws.send("E " + msg)
                    self.eventCache.pop(idx)
            except Exception:
                pass

    def on_message(self, message):
        if self.sockJsFraming:
            if self.debug and message.startswith("h"):
                logging.debug("♥")
            message = message[3:-2]
        if message in self.MSBMessageTypes:
            logging.info(message)
            if message == "IO_CONNECTED":
                if self.reconnecting:
                    self.reconnecting = False
                    if self.sockJsFraming:
                        _selfd = json.dumps(
                            self.objectToJson(self.getSelfDescription())
                        ).replace("\\n", "")
                        self.ws.send('["R ' + _selfd[1:-1] + '"]')
                    else:
                        self.ws.send(
                            "R " + self.objectToJson(self.getSelfDescription())
                        )
            if message == "IO_REGISTERED":
                self.registered = True
                if self.eventCacheEnabled:
                    self.connected = True
                    self.sendBuf()
            elif message == "NIO_ALREADY_CONNECTED":
                if self.connected:
                    try:
                        self.ws.close()
                    except Exception:
                        pass
            elif message == "NIO_UNEXPECTED_REGISTRATION_ERROR":
                if self.connected:
                    try:
                        self.ws.close()
                    except Exception:
                        pass
            elif message == "NIO_UNAUTHORIZED_CONNECTION":
                if self.connected:
                    try:
                        self.ws.close()
                    except Exception:
                        pass
            elif message == 'ping':
                if self.sockJsFraming:
                    self.ws.send('["pong"]')
                else:
                    self.ws.send('pong')
        if message.startswith("C"):
            jmsg = message.replace('\\"', '"')
            jmsg = json.loads(jmsg[2:])
            logging.info(str(jmsg))
            if jmsg["functionId"] not in self.functions:
                if jmsg["functionId"].startswith("/") and not jmsg[
                    "functionId"
                ].startswith("//"):
                    jmsg["functionId"] = jmsg["functionId"][1:]
            if jmsg["functionId"] in self.functions:
                if "correlationId" in jmsg:
                    jmsg["functionParameters"]["correlationId"] = jmsg["correlationId"]
                else:
                    logging.debug("correlationid could not be found. Does the websocket interface version support it?")
                self.functions[jmsg["functionId"]].implementation(
                    jmsg["functionParameters"]
                )
            else:
                logging.warning("Function could not be found: " + jmsg["functionId"])
        elif message.startswith("K"):
            jmsg = message.replace('\\"', '"')
            jmsg = json.loads(jmsg[2:])
            logging.info(str(jmsg))
            logging.debug("CONFIGURATION: " + str(jmsg))
            if jmsg["uuid"] == self.uuid:
                for key in jmsg["params"]:
                    if key in self.configuration["parameters"]:
                        self.changeConfigParameter(key, jmsg["params"][key])
                self.reRegister()

    def on_error(self, error):
        logging.error(error)

    def on_close(self, code, reason):
        logging.debug("DISCONNECTED")
        logging.debug("Websocket Close Status Code: (" + str(code) + "); Reason: (" + str(reason) + ")")
        self.connected = False
        self.registered = False
        if self.autoReconnect and not self.userDisconnect:
            logging.info(
                "### closed, waiting "
                + str(self.reconnectInterval)
                + " seconds before reconnect. ###"
            )
            time.sleep(self.reconnectInterval)
            self.reconnecting = True
            logging.info("Start reconnecting to msb url: >" + self.msb_url + "<")
            self.connect(self.msb_url)

    def on_open(self):
        logging.debug("Socket open")
        self.connected = True

    def enableDebug(self, debug=True):
        """Enables or disables the debug logging for the msb client.

        Args:
            debug (bool): Used to either enable (true) or disable (false) debug logging.
        """
        if debug:
            logging.basicConfig(
                format="[%(asctime)s] %(module)s %(name)s.%(funcName)s"
                + " +%(lineno)s: %(levelname)-8s [%(process)d] %(message)s"
            )
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            logging.basicConfig(format="[%(asctime)s] %(message)s")
            logging.getLogger().setLevel(logging.INFO)
        self.debug = debug

    def enableTrace(self, trace=True):
        """Enables or disables the websocket trace.

        Args:
            trace (bool): Used to either enable (true) or disable (false) websocket trace
        """
        self.trace = trace
        websocket.enableTrace(trace)

    def enableDataFormatValidation(self, dataFormatValidation=True):
        """Enables or disables data format and message format validation.

        (Mainly for development, can be disabled in production to improve performance)

        Args:
            dataFormatValidation (bool): Used to either enable (true) or disable (false) format validation
        """
        self.dataFormatValidation = dataFormatValidation

    def disableAutoReconnect(self, autoReconnect=True):
        """Disables or enables auto reconnect for the client if connection to MSB gets lost.

        Args:
            autoReconnect (bool): Used to either disable (true) or enable (false) auto reconnect
        """
        self.autoReconnect = not autoReconnect

    def setReconnectInterval(self, interval=10000):
        """Set the interval in ms for automatic reconnects if connection to MSB gets lost.

        Args:
            interval (int):  The interval value in ms (>=3000) for automatic reconnections
        """
        if interval <= 3000:
            interval = 3000
        self.reconnectInterval = interval / 1000

    def setKeepAlive(self, keepAlive=True, heartbeat_interval=8000):
        """Sets the keepalive interval for the client-side heartbeat in ms for the WS connection.

        This is required if there is no server-side heartbeat.

        Args:
            keepAlive (bool):  Used to enable (true) or disable (false) the keep alive functionality
            heartbeat_interval (int):  Client-side heartbeat interval value in ms
        """
        self.keepAlive = keepAlive
        if heartbeat_interval < 8000:
            heartbeat_interval = 8000
        self.heartbeat_interval = heartbeat_interval / 1000

    def disableSockJsFraming(self, sockJsFraming=True):
        """Disables or enables the sockJs framing.

        Args:
            sockJsFraming (bool): Used to either disable (true) or enable (false) sockJs framing
        """
        self.sockJsFraming = not sockJsFraming

    def disableHostnameVerification(self, hostnameVerification=True):
        """Disables or enables checking for self-signed SSL certificates (disable it e.g. for development)

        Args:
            hostnameVerification (bool): Used to either disable (true) or enable (false) ssl checks
        """
        self.hostnameVerification = not hostnameVerification

    def disableEventCache(self, disableEventCache=True):
        """Disables or enables the event cache, which will save sent events if no active MSB connection is present.

        Args:
            disableEventCache (bool): Used to either disable (true) or enable (false) event cache
        """
        self.eventCacheEnabled = not disableEventCache

    def setEventCacheSize(self, eventCacheSize=1000):
        """Sets the size (max number of events) of the event cahe.

        If the max is reached, oldest entry gets dismissed.

        Args:
            eventCacheSize (int): The size of the event cache (event entries)
        """
        self.eventCacheSize = eventCacheSize

    def enableThreadAsDaemon(self, threadAsDaemonEnabled=True):
        """Enable the msb client thread to run as daemon.

        This will run the websocket thread as daemon to be independet from the user threads.

        Args:
            threadAsDaemonEnabled (bool): Used to either enable (true) or disable (false) the thread to run as daemon
        """
        self.threadAsDaemonEnabled = threadAsDaemonEnabled

    def _checkUrl(self, msb_url=None):
        """Checks and transforms the msb url into a valid websocket format

        Args:
            msb_url (str): The url of the MSB (http(s)://host:port or ws(s)://host:port)
        """
        server_id = str(randint(100, 999))
        session_id = str(uuid.uuid4()).replace("-", "")
        if msb_url is not None:
            self.msb_url = msb_url
        if "http://" in self.msb_url:
            self.msb_url = self.msb_url.replace("http://", "ws://")
        elif "https://" in self.msb_url:
            self.msb_url = self.msb_url.replace("https://", "wss://")
        if not (self.msb_url.startswith("ws://") or self.msb_url.startswith("wss://")):
            logging.error("WRONG MSB URL FORMAT: " + str(self.msb_url))
        if self.sockJsFraming:
            self.msb_url_with_wspath = (
                self.msb_url
                + "/websocket/data/"
                + server_id
                + "/"
                + session_id
                + "/websocket"
            )
        else:
            self.msb_url_with_wspath = self.msb_url + "/websocket/data/websocket"

    def connect(self, msb_url=None):
        """Connects the client to the MSB WebSocket interface.

        Args:
            msb_url (str): The url of the MSB (http(s)://host:port or ws(s)://host:port)
        """
        self.userDisconnect = False

        # check and update the url fromat
        self._checkUrl(msb_url)
        # init the websocket app and register own listeners
        ws = websocket.WebSocketApp(
            self.msb_url_with_wspath,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.ws = ws
        ws.on_open = self.on_open

        # prepare and start socket
        def runf():
            try:
                if not self.hostnameVerification:
                    if self.keepAlive:
                        ws.run_forever(
                            ping_interval=self.heartbeat_interval,
                            ping_timeout=self.heartbeat_interval - 5,
                            sslopt={
                                "cert_reqs": ssl.CERT_NONE,
                                "check_hostname": False,
                            },
                            suppress_origin=True
                        )
                    else:
                        ws.run_forever(
                            sslopt={
                                "cert_reqs": ssl.CERT_NONE,
                                "check_hostname": False,
                            },
                            suppress_origin=True
                        )
                else:
                    if self.keepAlive:
                        ws.run_forever(
                            ping_interval=self.heartbeat_interval,
                            ping_timeout=self.heartbeat_interval - 3,
                        )
                    else:
                        ws.run_forever()
            except Exception:
                pass

        logging.info("Connecting to MSB @ " + self.msb_url)
        wst = threading.Thread(target=runf)
        if self.threadAsDaemonEnabled:
            wst.setDaemon(True)
        wst.start()

    def disconnect(self):
        """Disconnects the client from the MSB WebSocket interface."""
        self.userDisconnect = True
        logging.debug("Disconnect requested by msb client api")
        self.ws.close()

    def register(self):
        """Sends registration message to the MSB."""
        def _sendReg():
            if self.sockJsFraming:
                _selfd = json.dumps(
                    self.objectToJson(self.getSelfDescription())
                ).replace("\\n", "")
                _selfd = _selfd[1:-1]
                self.ws.send('["R ' + _selfd + '"]')
            else:
                self.ws.send("R " + self.objectToJson(self.getSelfDescription()))

        def _set_interval(func, sec):
            def func_wrapper():
                if self.connected:
                    func()
                else:
                    _set_interval(func, sec)

            t = threading.Timer(sec, func_wrapper)
            t.start()
            return t

        _set_interval(_sendReg, 0.1)

    def addEvent(
        self,
        event,
        event_name=None,
        event_description=None,
        event_dataformat=None,
        event_priority=0,
        isArray=None,
    ):
        """Adds an event to the self-description.

        Args:
            event (:obj:Event, str): The event object or the event id
            event_name (str): The name of the event
            event_description (str): The description of the event
            event_dataFormat (:obj:): The data type of the event (of class DataFormat, DataType or ComplexDataFormat)
            event_priority (str, int): The priority of the event (LOW,MEDIUM,HIGH) or (0,1,2)
            isArray (bool): Specifies if the event handles an object array or just an object of the data
        """
        # create event object by single params
        if not isinstance(event, Event):
            event = Event(
                event,
                event_name,
                event_description,
                event_dataformat,
                event_priority,
                isArray,
            )
        # for complex objects, update dataformat
        if event.dataFormat is not None:
            # if array of complex objects, change dataformat to type array
            if event.isArray:
                if "$ref" in event.dataFormat["dataObject"]:
                    event.dataFormat["dataObject"]["type"] = "array"
                    event.dataFormat["dataObject"]["items"] = {}
                    event.dataFormat["dataObject"]["items"]["$ref"] = {}
                    event.dataFormat["dataObject"]["items"][
                        "$ref"
                    ] = event.dataFormat["dataObject"]["$ref"]
                    del event.dataFormat["dataObject"]["$ref"]
            # if not an array of complex objects, change dataformat to type object
            elif not event.isArray:
                if "$ref" in event.dataFormat["dataObject"]:
                    event.dataFormat["dataObject"]["type"] = "object"
        # logging.debug(str(event.dataFormat))
        # validate data format and add event
        if vadilateEventDataFormat(event.dataFormat):
            event.id = len(self.events) + 1
            if event.eventId not in self.events:
                self.events[event.eventId] = event
            else:
                logging.error(
                    str(event.eventId) + " already in events, change event id!"
                )
                raise Exception("Event with this ID already present: " + str(event.eventId))

    def addFunction(
        self,
        function,
        function_name=None,
        function_description=None,
        function_dataformat=None,
        fnpointer=None,
        isArray=False,
        responseEvents=None,
    ):
        """Adds a function to the self-description.

        Args:
            function (:obj:Function, str): The function object ot the function id
            function_name (str): The name of the function
            function_description (str): The description of the function
            function_dataformat (:obj:): The data type of the function (of class DataFormat or ComplexDataFormat)
            fnpointer (:func:): The function implementation to be called for incoming events
            isArray (bool): Specifies if the function handles an object array or just an object of the data
            responseEvents (:obj: list of event ids): The list of event IDs to be send as response events
        """
        # create function object by single params
        if not isinstance(function, Function):
            function = Function(
                function,
                function_name,
                function_description,
                function_dataformat,
                fnpointer,
                isArray,
                responseEvents,
            )
        # check if defined reponseEvents are valid (exist)
        if function.responseEvents is not None:
            for responseEvent in function.responseEvents:
                if responseEvent not in self.events:
                    logging.error(
                        "Event not found for id " + responseEvent
                    )
                    raise Exception("Event not found for id " + responseEvent)
        # for complex objects, update dataformat
        if function.dataFormat is not None:
            # if array of complex objects, change dataformat to type array
            if function.isArray:
                if "$ref" in function.dataFormat["dataObject"]:
                    function.dataFormat["dataObject"]["type"] = "array"
                    function.dataFormat["dataObject"]["items"] = {}
                    function.dataFormat["dataObject"]["items"]["$ref"] = {}
                    function.dataFormat["dataObject"]["items"][
                        "$ref"
                    ] = function.dataFormat["dataObject"]["$ref"]
                    del function.dataFormat["dataObject"]["$ref"]
            # if not and array of complex objects, change dataformat to type object
            elif not function.isArray:
                if "$ref" in function.dataFormat["dataObject"]:
                    function.dataFormat["dataObject"]["type"] = "object"
        # logging.debug(str(function.dataFormat))
        # validate data format and add function
        if vadilateFunctionDataFormat(function.dataFormat):
            if function.functionId not in self.functions:
                self.functions[function.functionId] = function
            else:
                logging.error(
                    str(function.functionId)
                    + " already in functions, change function id!"
                )
                raise Exception("Function with this ID already present: " + str(function.functionId))

    def setEventValue(self, eventId, eventValue):
        """Sets the value for an event

        Args:
            eventId (str): The event id
            eventValue (str): The value of the event
        """
        if eventId in self.events:
            self.events[eventId].dataObject = eventValue

    def publish(
        self,
        eventId,
        dataObject=None,
        priority=None,
        cached=False,
        postDate=None,
        correlationId=None,
    ):
        """This function sends the event of the provided event ID.

        Optionally the value can be provided, otherwise the last set value will be used.
        The priority can also be set, otherwise the standard value for the event's priority will be used.
        A postDate can be optionally provided, otherwise the current timestamp will be used.

        Args:
            eventId (str): The event id
            dataObject (:obj:): The value to be published
            priority (str, int): The priority of the event (LOW,MEDIUM,HIGH) or (0,1,2)
            cached (bool): Specifies wether this event will be added to cache if MSB is currently not reachable
            postDate (datetime): the post date of the event (e.g. datetime.datetime.utcnow().isoformat()[:-3] + "Z")
            correlationId (str): The correlation id of the event used to idetify events in multi-step flows
        """
        event = {}
        event["uuid"] = self.uuid
        event["eventId"] = eventId
        # upfate the event value
        if dataObject is not None:
            self.events[eventId].dataObject = dataObject
            event["dataObject"] = self.events[eventId].dataObject
        if priority is not None:
            self.events[eventId].priority = priority
        event["priority"] = self.events[eventId].priority
        if postDate is None:
            event["postDate"] = datetime.datetime.utcnow().isoformat()[:-3] + "Z"
        else:
            event["postDate"] = str(postDate)
        if correlationId is not None:
            event["correlationId"] = correlationId

        # validate event value
        if self.dataFormatValidation and dataObject is not None:
            self.validateValueForDataFormat(
                event["dataObject"],
                self.events[eventId].df,
                self.events[eventId].dataFormat,
                self.events[eventId].isArray,
            )
        msg = self.objectToJson(event)

        # send event
        if self.connected and self.registered:
            try:
                if self.sockJsFraming:
                    _msg = self.objectToJson(msg).replace("\\n", "")
                    self.ws.send('["E ' + _msg[1:-1] + '"]')
                else:
                    self.ws.send("E " + msg)
                logging.debug("SENDING: " + msg)
            except Exception:
                logging.exception(self, "Error, could not send message...")
                pass
        else:
            # or cache event if not connected
            if self.eventCacheEnabled and cached:
                logging.debug(
                    "Not connected and/or registered, putting event in cache."
                )
                if len(self.eventCache) < self.eventCacheSize:
                    self.eventCache.append(msg)
                else:
                    self.eventCache.pop(0)
                    self.eventCache.append(msg)
            elif cached and not self.eventCacheEnabled:
                logging.debug(
                    "Global cache disabled, message cache flag overridden and discarded."
                )
            else:
                logging.debug("Caching disabled, message discarded.")

    @staticmethod
    def validateValueForDataFormat(value, df, dataFormat, isArray):
        """Validate the event value to match the specified data format

        Args:
            value (:obj:): The value of the event to be validated
            df (:obj:): The (short) data format of the event
            dataFormat (:obj:): The (complex) data format of the event
            isArray (bool): Specifies wether this event will be added to cache if MSB is currently not reachable
        """
        if isinstance(df, ComplexDataFormat):
            if validateValueForComplexDataformat(
                value,
                dataFormat,
                isArray,
            ):
                return True
            else:
                return False
        else:
            if validateValueForSimpleDataformat(
                value,
                df,
                isArray,
            ):
                return True
            else:
                return False

    def addConfigParameter(self, key, value, type):
        """Add a new configuration parameter to the client.

        Configuration parameters can be used to change client behaviour ny changing its values via MSB GUI.

        Args:
            key (str): The key (name) of the configuration parameter
            value (:obj:): The initial value of the configuration parameter
            type (:obj:DataType): The simple data format of the confituration parameter
        """
        newParam = getDataType(type)
        newParam["type"] = newParam["type"].upper()
        if "format" in newParam:
            newParam["format"] = newParam["format"].upper()
        if "format" in newParam and newParam["format"] == "DATE-TIME":
            newParam["value"] = str(value)
        else:
            newParam["value"] = value
        self.configuration["parameters"][key] = newParam

    def getConfigParameter(self, key):
        """Get the value of a configuration parameter.

        Args:
            key (str): The key (name) of the configuration parameter
        """
        if key in self.configuration["parameters"]:
            return self.configuration["parameters"][key]["value"]
        else:
            logging.warning(
                "Cannot get config param for unknown key: " + str(key)
            )
            raise Exception("Cannot get config param for unknown key: " + str(key))

    def changeConfigParameter(self, key, value):
        """Change the value of a configuration parameter.

        Args:
            key (str): The key (name) of the configuration parameter
            value (:obj:): The new value of the configuration parameter
        """
        if key in self.configuration["parameters"]:
            oldValue = self.configuration["parameters"][key]["value"]
            if oldValue != value:
                self.configuration["parameters"][key]["value"] = value
                if self.connected and self.registered:
                    self.reRegister()
            else:
                logging.warning(
                    "Cannot change config param. Value is already set!"
                )
        else:
            logging.warning(
                "Cannot change config param for unknown key: " + str(key)
            )

    def reRegister(self):
        """Performs a new registration to update the self-description on MSB."""
        logging.debug("Reregistering after configuration parameter change...")
        if self.sockJsFraming:
            _selfd = json.dumps(self.objectToJson(self.getSelfDescription())).replace(
                "\\n", ""
            )
            self.ws.send('["R ' + _selfd[1:-1] + '"]')
        else:
            self.ws.send("R " + self.objectToJson(self.getSelfDescription()))

    def objectToJson(self, object):
        """Converts a python object into a json object.

         Returns:
            json object: The resulting json object
        """
        return json.dumps(object, default=lambda o: o.__dict__, indent=4)

    def jsonToObject(self, json):
        """Converts a json into a python object.

         Returns:
            python object: The resulting python object
        """
        return json.loads(object)

    def getSelfDescription(self):
        """Generate the self description JSON object of the application or smart object."""
        self_description = {}
        self_description["@class"] = self.service_type
        self_description["uuid"] = self.uuid
        self_description["name"] = self.name
        self_description["description"] = self.description
        self_description["token"] = self.token
        _ev = []
        e_props = ["@id", "id", "dataFormat", "description", "eventId", "name"]
        for event in self.events:
            current_e_props = []
            # fix serialization issues "AttributeError: 'mappingproxy' object has no attribute '__dict__'"
            # caused by property "df" directly holding python datatypes (int, str, bool, ...)
            # Workaround: Deep copy event, set string value to property "df" before serializing
            msbEvent = copy.deepcopy(self.events[event])
            msbEvent.df = "non-serializable-workaround"
            e = json.loads(
                json.dumps(msbEvent, default=lambda o: o.__dict__, indent=4)
            )
            for key in list(e.keys()):
                if key == "id":
                    e["@id"] = e["id"]
                    del e[key]
            del e["priority"]
            del e["df"]
            if e["dataFormat"] is None:
                del e["dataFormat"]
            del e["isArray"]
            for key in list(e.keys()):
                current_e_props.append(key)
            for key in current_e_props:
                if key not in e_props:
                    # logging.warning(self, 'Remove key from event if invalid in self description: ' + key)
                    try:
                        del e[key]
                    except Exception:
                        logging.exception(self, "Key not found: " + key)
            _ev.append(e)
        self_description["events"] = _ev
        _fu = []
        for function in self.functions:
            f = json.loads(
                json.dumps(self.functions[function], default=lambda o: o.__dict__, indent=4)
            )
            if f["responseEvents"] and len(f["responseEvents"]) > 0:
                _re = []
                for idx, re in enumerate(f["responseEvents"]):
                    _re.append(self.events[re].id)
                f["responseEvents"] = _re
            else:
                del f["responseEvents"]
            del f["isArray"]
            if "implementation" in f:
                del f["implementation"]
            if f["dataFormat"] is None:
                del f["dataFormat"]
            _fu.append(f)
        self_description["functions"] = _fu
        self_description["configuration"] = self.configuration
        return self_description

    def readConfig(self):
        """Helper function to parse main configuration param by param name from the application.properties file"""
        logging.info("Reading configuration from application.properties file")
        config = None
        if self.applicationPropertiesCustomPath is None:
            config = open("application.properties", "r")
        else:
            config = open(str(self.applicationPropertiesCustomPath), "r")
        if config is not None:
            for line in config:
                configparam = line.split("=")
                if configparam[0] == "msb.type":
                    self.service_type = configparam[1].rstrip()
                elif configparam[0] == "msb.name":
                    self.name = configparam[1].rstrip()
                elif configparam[0] == "msb.uuid":
                    self.uuid = configparam[1].rstrip()
                elif configparam[0] == "msb.token":
                    self.token = configparam[1].rstrip()
                elif configparam[0] == "msb.url":
                    self.msb_url = configparam[1].rstrip()
                elif configparam[0] == "msb.description":
                    self.description = configparam[1].rstrip()


def vadilateEventDataFormat(df):
    """Validates the specified dataformat of an event by using a json schema

    Args:
        df (:obj:): The data format specified for the event
    """
    if df is None:
        return True
    schema_file = os.path.join(os.path.dirname(__file__), "event_schema.json")
    schema = json.loads(open(schema_file).read())
    do = {"definitions": json.loads(json.dumps(df, default=lambda o: o.__dict__, indent=4))}
    try:
        jsonschema.Draft4Validator(schema).validate(do)
    except Exception as e:
        logging.exception(e)
        return False
    return True


def vadilateFunctionDataFormat(df):
    """Validates the specified dataformat of a function by using a json schema

    Args:
        df (:obj:): The data format specified for the function
    """
    if df is None:
        return True
    schema_file = os.path.join(os.path.dirname(__file__), "function_schema.json")
    schema = json.loads(open(schema_file).read())
    do = {"definitions": json.loads(json.dumps(df, default=lambda o: o.__dict__, indent=4))}
    try:
        jsonschema.Draft4Validator(schema).validate(do)
    except Exception as e:
        logging.exception(e)
        return False
    return True


def validateValueForComplexDataformat(value, dataFormat, isArray):
    """Validate the event value to match the specified complex data format

    Args:
        value (:obj:): The value of the event to be validated
        dataFormat (:obj:): The (complex) data format of the event
        isArray (bool): Specifies wether this event will be added to cache if MSB is currently not reachable
    """
    schema = {}
    if isArray:
        schema["items"] = {}
        schema["items"]["$ref"] = dataFormat["dataObject"]["items"]["$ref"]
        schema["type"] = "array"
    else:
        schema["$ref"] = {}
        schema["$ref"] = dataFormat["dataObject"]["$ref"]
        schema["type"] = "object"
    schema["definitions"] = dataFormat
    try:
        jsonschema.validate(
            value,
            schema,
            format_checker=jsonschema.FormatChecker(),
        )
        return True
    except Exception as e:
        logging.error(
            "Error validating event: "
            + str(e)
        )
        return False


def validateValueForSimpleDataformat(value, df, isArray):
    """Validate the event value to match the specified simple data format

    Args:
        value (:obj:): The value of the event to be validated
        df (:obj:): The (short) data format of the event
        isArray (bool): Specifies wether this event will be added to cache if MSB is currently not reachable
    """
    if isArray:
        try:
            if all((type(item) == df) for item in value):
                return True
            else:
                logging.error(
                    "Error validating event: "
                    + "Value in list doesn't fit the required data format: "
                    + str(value)
                    + ", expected all items to be: "
                    + str(df)
                )
                return False
        except Exception:
            logging.error(
                "Error validating event: "
                + "Value ("
                + str(value)
                + ") is not an array as defined."
            )
            return False
    else:
        if type(value) == df:
            return True
    logging.error(
        "Error validating event: "
        + "Value doesn't fit the required data format: "
        + str(value)
        + " = "
        + str(type(value))
        + ", expected: "
        + str(df)
    )
    return False
