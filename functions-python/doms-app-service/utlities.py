import datetime
import time
from datetime import datetime, date
from logger import logInfo, logDebug, logError, logException

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