<p align="center">
  <a href="https://research.virtualfortknox.de" target="_blank" rel="noopener noreferrer">
    <img src="https://research.virtualfortknox.de/static/cms/img/vfk_research_logo.png" alt="VFK Research Logo" height="70" >
  </a>
</p>

# MSB websocket client library for Python

[![Build Status](https://app.travis-ci.com/research-virtualfortknox/msb-client-websocket-python.svg?branch=master)](https://app.travis-ci.com/research-virtualfortknox/msb-client-websocket-python)
[![PyPI version](https://badge.fury.io/py/msb-client-websocket-python.svg)](https://badge.fury.io/py/msb-client-websocket-python)
[![Coverage Status](https://coveralls.io/repos/github/research-virtualfortknox/msb-client-websocket-python/badge.svg?branch=feature-coveralls)](https://coveralls.io/github/research-virtualfortknox/msb-client-websocket-python?branch=feature-coveralls)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fresearch-virtualfortknox%2Fmsb-client-websocket-python.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fresearch-virtualfortknox%2Fmsb-client-websocket-python?ref=badge_shield)

**Compatibility Matrix**

Client version compatibility to MSB versions:

| | **1.5.x-RELEASE** | **1.6.x-RELEASE** |
|---|:---:|:---:|
| 1.0.x       | x | x |

## Welcome

If you want to contribute, please read the [Contribution Guidelines](.github/CONTRIBUTING.md).

If you want to test this client by using its sources and a sample app, read the [App Sample](doc/app_sample.md).

If you want to know how to use this client in your own project, read below.

## What is VFK MSB

TODO: Link to general documentation about VFK MSB

You can use this client to connect a python app to VFK MSB.

## Prerequisites

* Setup [Python](https://www.python.org/downloads/) **version 3.7.x** (last client version supporting Python 2.7 is v1.0.8, last client version supporting Python 3.6 is v1.0.11)
* MSB client installed using PyPi
* Optional: Use pipenv to run your python app in a virtual environment to avoid dependency isssues with other apps

Install MSB client from PyPi

```sh
pip install msb-client-websocket-python
```

Import to your applicaton

```python
from msb_client.ComplexDataFormat import ComplexDataFormat
from msb_client.DataType import DataType
from msb_client.Event import Event
from msb_client.Function import Function
from msb_client.MsbClient import MsbClient
```

## Create self-description

The figure below shows a minimal required `self-description model` of a smart object / application.
Every smart object / application requires (must have) a uuid and a token.
The uuid is competent for identification
and the token is used to verify the smart object / application for its owner on the MSB side.

![Self Description](doc/images/self-description.png)

TODO: Here you can find more information about
the `self-description structure` and `supported data formats`.

### Alternative 1 - By application.properties

Add the main description by adding an `application.poperties` file to the root of your project:

Generate the uuid e.g. by a tool like https://www.uuidgenerator.net/

```sh
msb.uuid=76499d88-34cf-4836-8cc1-7e0d9c54dacx
msb.name=YourSmartObjectName
msb.description=YourSmartObjectDesc
msb.token=5e0d9c54dacx
msb.type=SmartObject
```

When initializing your msb client instance, the `application.properties` file will be loaded.

```python
myMsbClient = MsbClient()
```

You can also set a custom path to the `application.properties` file.

```python
myMsbClient = MsbClient(applicationPropertiesCustomPath="./your/path/to/application.properties")
```

### Alternative 2 - By constructor

If you do not provide an application.properties file, use the constructor
to define the basic self description.

```python
SERVICE_TYPE = "SmartObject"
SO_UUID = str(uuid.uuid1()) # you can type in an own uuid here instead of generating it
SO_NAME = "YourSmartObjectName"
SO_DESCRIPTION = "YourSmartObjectDesc"  
SO_TOKEN = SO_UUID[-6:]
myMsbClient = MsbClient(
    SERVICE_TYPE,
    SO_UUID,
    SO_NAME,
    SO_DESCRIPTION,
    SO_TOKEN,
)
```

## Add Events

Add `events` to your smart object / application which can be send to MSB.

### Alternative 1: Simple event creation sample (using method params):

```python
event_id = "E1"
event_name = "EVENT " + event_id
event_description = "EVENT Description " + event_id
event_dataformat = DataType.STRING
event_priority = 1 # 0 (LOW), 1 (MEDIUM), 2 (HIGH)
isArray = False # just one value or array of it?

# add the event
myMsbClient.addEvent(
    event_id,
    event_name,
    event_description,
    event_dataformat,
    event_priority,
    isArray,
)
```

### Alternative 2: Complex event creation sample (using object):

```python
event_id = "E2"
event_name = "EVENT " + event_id
event_description = "EVENT Description " + event_id
event_priority = 1 # 0 (LOW), 1 (MEDIUM), 2 (HIGH)
isArray = False # just one value or array of it?

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

# add the event (with the root of the nested complex object)
myMsbClient.addEvent(
    event_id,
    event_name,
    event_description,
    myDevice,
    event_priority,
    isArray,
)
```

### Alternative 3: Complex event creation sample (using json object):

```python
event_id = "E3"
event_name = "EVENT " + event_id
event_description = "EVENT Description " + event_id
event_priority = 1 # 0 (LOW), 1 (MEDIUM), 2 (HIGH)
isArray = False # just one value or array of it?

# add the event (with the MSB-ready json object)
myMsbClient.addEvent(
    event_id,
    event_name,
    event_description,
    {
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
        "dataObject" : {
            "$ref" : "#/definitions/Team"
        }
    },
    event_priority,
    isArray,
)
```

See `app_sample.py` for more event creation examples.

## Add Functions

Add `functions` and their implementations your smart object / application is able to handle.

### Alternative 1: Simple function creation sample (using method params):

```python
function_id = "F1"
function_name = "FUNC " + function_id
function_description = "FUNC Description " + function_id
function_dataformat = DataType.STRING
isArray = False # handle array of values or just one value?
responseEvents = None # you can link to response events here by a list of event is e.g. ["E1"]

# define the function which will be passed to the function description
# this function implementation will be called
def printMsg(msg):
    print(str(msg["dataObject"]))

# add the function
myMsbClient.addFunction(
    function_id,
    function_name,
    function_description,
    function_dataformat,
    printMsg,
    isArray,
    responseEvents,
)
```

### Alternative 2: Complex function creation sample (using object):

```python
function_id = "F2"
function_name = "FUNC " + function_id
function_description = "FUNC Description " + function_id
isArray = False # handle array of values or just one value?
responseEvents = None # you can link to response events here by a list of event is e.g. ["E1"]

# define a complex data format to be used in an event
# init the complex data format
myCar = ComplexDataFormat("MyCar")

# add the properties to the complex objects
# (property_name, property_datatype, isArray)
myCar.addProperty("carColor", DataType.STRING, False)
myCar.addProperty("carNrOfSeats", DataType.INT32, False)
myCar.addProperty("carWeight", DataType.FLOAT, False)

# define the function which will be passed to the function description
# this function implementation will be called
def printMsg(msg):
    print(str(msg["dataObject"]))

# add the function
myMsbClient.addFunction(
    function_id,
    function_name,
    function_description,
    myCar,
    printMsg,
    isArray,
    responseEvents,
)
```

### Alternative 3: Complex function creation sample (using json object):

```python
function_id = "F3"
function_name = "FUNC " + function_id
function_description = "FUNC Description " + function_id
isArray = False # handle array of values or just one value?
responseEvents = None # you can link to response events here by a list of event is e.g. ["E1"]

# define the function which will be passed to the function description
# this function implementation will be called
def printMsg(msg):
    print(str(msg["dataObject"]))

# add the function
myMsbClient.addFunction(
    function_id,
    function_name,
    function_description,
    {
        "MyCar" : {
            "type" : "object",
            "properties" : {
                "carColor" : {
                    "type" : "string"
                },
                "carNrOfSeats" : {
                    "format": "int32",
                    "type": "integer"
                },
                "carWeight" : {
                    "format": "float",
                    "type": "number"
                },
                "wheels" : {
                    "type" : "array",
                    "items" : {
                        "$ref" : "#/definitions/MyWheel"
                    }
                }
            }
        },
        "MyWheel" : {
            "type" : "object",
            "properties" : {
                "position" : {
                    "enum" : [ "br", "bl", "fr", "fl" ],
                    "type" : "string"
                }
            }
        },
        "dataObject" : {
            "$ref" : "#/definitions/MyCar"
        }
    },
    printMsg,
    isArray,
    responseEvents,
)
```

See `app_sample.py` of the application template for more (and complex) examples.

## Connect and Register Client

```python
msb_url = 'ws://127.0.0.1:8085'
myMsbClient.connect(msb_url)
myMsbClient.register()
```

You will get an `IO_CONNECTED` and `IO_REGISTERED` event from MSB, if successful.

## Event publishing

For publishing an event to a websocket broker interface,
only the `eventId` and `data` are required of the already specified event (see above).

```python
event_id = "E1"
event_value = 'Hello World!'

myMsbClient.publish(
  event_id, 
  event_value
)
```

The MSB responds with an `IO_PUBLISHED` event, if successful.

By default events are published with a low priority.

It is also possible to `set the priority` of an event.

There are three possible priorities for events like it is shown at the following table.

| `Constant` | `Value` |
|:---:|:---:|
| LOW | 0 |
| MEDIUM| 1 |
| HIGH| 2 |

```python
event_id = "E1"
event_value = 'Hello World!'
event_priority = 2

myMsbClient.publish(
  event_id, 
  event_value,
  event_priority
)
```

Another option is to publish an event as `cached event` by setting the cache parameter to true.
And you can add a `post date`.

This means that the event is not deleted if the connection is broken.

```python
event_id = "E1"
event_value = 'Hello World!'
event_priority = 2
event_isCached = True
event_postDate = datetime.datetime.utcnow().isoformat()[:-3] + "Z"

myMsbClient.publish(
  event_id, 
  event_value,
  event_priority,
  event_isCached,
  event_postDate
)
```

You cann also handle `correlation ids` to identify an event among flows.

```python
event_id = "E1"
event_value = 'Hello World!'
event_priority = 2
event_isCached = True
event_postDate = datetime.datetime.utcnow().isoformat()[:-3] + "Z"
event_correlationId = "72047f33-a9ae-4aa5-b7ae-c1c4a2797cac"

myMsbClient.publish(
  event_id, 
  event_value,
  event_priority,
  event_isCached,
  event_postDate,
  event_correlationId
)
```

For values based on complex data formats it will look like this:

```python
event_id = "E2"
event_priority = 2
event_isCached = True
event_postDate = datetime.datetime.utcnow().isoformat()[:-3] + "Z"
event_correlationId = "72047f33-a9ae-4aa5-b7ae-c1c4a2797cac"

# pepare the complex ovbject based on a complex data format
# use it as event value
myModuleObj = {}
myModuleObj['moduleName'] = 'Module 1'
myDeviceObj = {}
myDeviceObj['deviceName'] = 'Device 1'
myDeviceObj['deviceWeight'] = 1.3
myDeviceObj['submodules'] = [myModuleObj]

myMsbClient.publish(
  event_id, 
  myDeviceObj,
  event_priority,
  event_isCached,
  event_postDate,
  event_correlationId
)
```

## Function call handling

As shown above the addFunction method includes a `function pointer`
to point to the function implementation.

## Configuration parameters

Configuration parameters are a simple list of key value pairs for the smart object / application.
It is displayed and can be customized in the MSB UI to change your apps behaviour during runtime.

`Add` condifuration parameters:

```python
param_name_1 = "testParam1"
param_value_1 = True
param_datatype_1 = DataType.BOOLEAN
myMsbClient.addConfigParameter(param_name_1, param_value_1, param_datatype_1)

param_name_2 = "testParam2"
param_value_2 = "StringValue"
param_datatype_2 = DataType.STRING
myMsbClient.addConfigParameter(param_name_2, param_value_2, param_datatype_2)

param_name_3 = "testParam3"
param_value_3 = 1000
param_datatype_3 = DataType.INT32
myMsbClient.addConfigParameter(param_name_3, param_value_3, param_datatype_3)
```

`Get` configuration parameter (after changed in MSB UI) to change your app behaviour:

```python
# get by getConfigParameter using name as key
parameterValueFound_1 = myMsbClient.getConfigParameter(param_name_1)
parameterValueFound_2 = myMsbClient.getConfigParameter(param_name_2)
parameterValueFound_3 = myMsbClient.getConfigParameter(param_name_3)
```

## SSL/TLS connection configuration

To enable `SSL/TLS`, you need to specify wss:// or https:// in the URL instead of ws:// or http://.

Furthermore, it is necessary to specify a trust store in the client,
which contains the public certificate of the MSB interface, so that it is considered trustworthy.

```python
msb_url = 'wss://<hostname>:<port>'
myMsbClient.connect(msb_url)
myMsbClient.register()
```

If you use an IP instead of a public url during development,
it will be necessary to disable the hostname verification to connect via web socket secure.

```python
myMsbClient.disableHostnameVerification(True)  
```

## Connection recovery

If connection to the common websocket interface is broken the client performs a reconnect.

After a reconnect the registration at the MSB will be redone automatically by the client.

You can change this interval by setting an integer value in `ms` for the reconnect interval.

```python
myMsbClient.setReconnectInterval(10000)
```

Or you can disable the automatic reconnect.

```python
myMsbClient.disableAutoReconnect(True)
```

## Event caching

If the client loses the connection, the published events are cached in a queue.

After a successfull reconnection, the queued events are published to MSB (FIFO principle).
The default size of the queue is 1000 entries. The size can be changed:

```python
myMsbClient.setEventCacheSize(1000)
```

If no event caching is needed, you can disable it.

```python
myMsbClient.disableEventCache(True)
```

## Debug mode

To debug your clients communication with MSB, you can enable the debug mode

```python
myMsbClient.enableDebug(True)
```

To enable the trace of the websocket communication use also

```python
myMsbClient.enableTrace(True)
```

It mgiht be also helpful to enable data format validation, to check if an event value is valid

```python
myMsbClient.enableDataFormatValidation(True)
```


## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fresearch-virtualfortknox%2Fmsb-client-websocket-python.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fresearch-virtualfortknox%2Fmsb-client-websocket-python?ref=badge_large)
