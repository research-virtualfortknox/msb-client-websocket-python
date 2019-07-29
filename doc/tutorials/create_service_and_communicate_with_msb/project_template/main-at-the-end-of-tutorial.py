import datetime
import threading
import uuid
import time

from msb_client.ComplexDataFormat import ComplexDataFormat
from msb_client.DataType import DataType
from msb_client.Event import Event
from msb_client.Function import Function
from msb_client.MsbClient import MsbClient

def printMsg(msg):
    print(str(msg["dataObject"]))

if __name__ == "__main__":

    myMsbClient = MsbClient()

    myMsbClient.enableDebug(True)
    myMsbClient.disableHostnameVerification(True)
    myMsbClient.disableEventCache(False)

    myMsbClient.addEvent(
        event="event1", # event id
        event_name="Event Name",
        event_description="Event Description",
        event_dataformat=DataType.STRING,
    )

    myMsbClient.addFunction(
        function="function1", # function id
        function_name="Function Name",
        function_description="Function Description",
        function_dataformat=DataType.STRING,
        fnpointer=printMsg,
        isArray=False,
        responseEvents=None,
    )

    print(myMsbClient.objectToJson(myMsbClient.getSelfDescription()))
    
    myMsbClient.connect()

    myMsbClient.register()

    myMsbClient.publish(
        eventId="event1",
        dataObject="Hello World",
        priority=0,
        cached=True,
        postDate=None,
        correlationId=None,
    )
