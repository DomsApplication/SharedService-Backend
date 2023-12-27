import logging

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger()

def lambda_handler(event, context):
    try:
        logger.info('## ENVIRONMENT VARIABLES')
        logger.info(os.environ['AWS_REGION'])
        logger.info(context.invoked_function_arn)
        logger.info(context.invoked_function_arn.split(":")[4])
        logger.info('## EVENT')
        logger.info(event)
    except Exception as error:
        logger.exception('Exception in main function', error)


