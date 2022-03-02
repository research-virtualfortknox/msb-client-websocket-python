# Application Sample Guide

## Prerequisites

- Setup [Python](https://www.python.org/downloads/) **version 3.7.x**
- This MSB client project sources including app_sample.py downloaded

## Install python modules

Install the required python modules execute

```sh
$ python setup.py install
```

## Run sample application

To run the sample client enter

```sh
$ python app_sample.py
```

You should get this output, 
if a valid MSB host address has been provided 
and debugging is enabled (myMsbClient.enableDebug(True)):

```sh
  <self-description output as json string>
  Connecting to MSB @ ws://127.0.0.1:8085
  Socket open
  IO_CONNECTED
  IO_REGISTERED
  SENDING: {
      "dataObject": "Hello World!",
      "eventId": "EVENT1",
      "postDate": "2017-11-22T13:33:27.730605",
      "priority": 1,
      "uuid": "32801d88-34cf-4836-8cc1-7e999c5444c8"
  }
  IO_PUBLISHED
```

The application establishes a connection, registers and publishes a sample event, 
to which the MSB sends an acknowledgement response (IO_PUBLISHED). 
The app_sample.py file is the main application file, 
you can extend it with your own code to add functionality 
or copy parts of it into your own application file.

## Description of the template files

The application template files and their function will be described in the following:

  - `app_sample.py` is the main class which is used to run the actual application.
  - `msb_client/MSBClient.py` is the client library which handles the websocket connection, 
  events and function calls and sends them to the application via an event emitter.
  - `application.properties` is an optional file, 
  it can be used to define the config parameters of the smart object or application, 
  like the UUID, object name, description or broker url from an external source, 
  e.g. configuration of a Docker container.
  - `setup.py` contains all the meta information for the python app which allows 
  to automatically install all needed dependencies and install the app as system library.

## Write your own application

If you checked out our appolication sample, you are ready to write your own application.

Visit [README.md](/../../) on our main page  for instrcutions how to integrate the msb client to your own applicaton using PyPi.