import datetime
import time
from datetime import datetime, date
from aws_lambda_powertools.event_handler import ( Response, content_types, )
from DomsException import DomsException

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

def sendResponse(code, body):
    return Response(
        status_code=code, 
        content_type=content_types.APPLICATION_JSON, 
        body= body
        )

def validateDataObject(_object: dict):
    if _object is None:
        message = f"Data-Object body is required."
        raise DomsException(400, message)
    elif _object["entity"] is None or _object["title"] is None or _object["version"] is None or _object["type"] is None:
        message = f"Required field(s) is missed. Please contact Administrator."
        raise DomsException(400, message)
    else:
        return True    

def validateRequestBody(body: dict):
    if body is None:
        message = f"Request Body is required."
        raise DomsException(400, message)
    elif body.entity is None or body.unique_id is None:
        message = f"Required field entity / unique_id is missed."
        raise DomsException(400, message)
    else:
        return True    
