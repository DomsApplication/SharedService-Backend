import datetime
from datetime import datetime
from logger import logInfo, logDebug, logError, logException


def getDateTimeNow():
    now = datetime.now()
    return now.strftime("%m/%d/%Y, %H:%M:%S")

