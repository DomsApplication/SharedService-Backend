import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def logInfo(key, message):
    logger.info(key + ':::' +message)

def logError(key, exception):
    logger.error(key + ':::' + str(exception))
