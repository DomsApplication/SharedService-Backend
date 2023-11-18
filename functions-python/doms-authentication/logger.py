import traceback
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def logInfo(key, message):
    logger.info(':::'.join([key, str(message)]))

def logDebug(key, message):
    logger.debug(':::'.join([key, str(message)]))

def logError(key, exception):
    logger.error(':::'.join([key, str(exception)]))
