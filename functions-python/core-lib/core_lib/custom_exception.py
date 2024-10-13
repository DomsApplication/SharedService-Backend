class CustomException(Exception):

    def __init__(self, error_code=500, message=None):
        super().__init__(message)
        self.error_code = error_code
        self.message = message
    
    def __str__(self):
        return str(self.message) # __str__() obviously expects a string to be returned, so make sure not to send any other data types        
