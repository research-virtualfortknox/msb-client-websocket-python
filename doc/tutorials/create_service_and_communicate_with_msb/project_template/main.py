import datetime
import threading
import uuid
import time

from msb_client.ComplexDataFormat import ComplexDataFormat
from msb_client.DataType import DataType
from msb_client.Event import Event
from msb_client.Function import Function
from msb_client.MsbClient import MsbClient

if __name__ == "__main__":

    myMsbClient = MsbClient()

    myMsbClient.enableDebug(True)
    myMsbClient.disableHostnameVerification(True)
    myMsbClient.disableEventCache(False)

    print(myMsbClient.objectToJson(myMsbClient.getSelfDescription()))
    
    myMsbClient.connect()

    myMsbClient.register()