import datetime
import time
from datetime import datetime, date
from aws_lambda_powertools.event_handler import ( Response, content_types, )
from aws_lambda_powertools import Logger, Tracer

tracer = Tracer()
logger = Logger()

date_format = "%Y/%m/%d"
time_format = "%H:%M:%S"
date_time_format = "%Y/%m/%d, %H:%M:%S"

def getDateTimeNow():
    now = datetime.now()
    return now.strftime(date_time_format)

def getDateNow():
    now = datetime.now()
    return now.strftime(date_format)

def getTimeNow():
    now = datetime.now()
    return now.strftime(time_format)

def getCurrentDate():
    return date.today()

def getDateFromtimestamp(timestamp):
    return date.fromtimestamp(timestamp)

def getCurrentMilliSec():
    return round(time.time() * 1000)

@tracer.capture_method
def sendResponse(code, body):
    return Response(
        status_code=code, 
        content_type=content_types.APPLICATION_JSON, 
        body= body
        )

