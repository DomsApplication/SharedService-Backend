import logging

class Logger:
    @staticmethod
    def get_logger(name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)  # Set desired log level here
        
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        if not logger.handlers:
            logger.addHandler(handler)
        
        return logger
