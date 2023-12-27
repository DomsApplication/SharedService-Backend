import json
import jsonschema
from jsonschema import validate
from logger import logInfo, logDebug, logError, logException

# Get a JsonSchema 
def get_schema(entityName):
    schema = {
        "$schema":"http://json-schema.org/draft-04/schema#",
        "title":"user",
        "description":"A user request json",
        "type":"object",
        "properties":{
            "unique_id":{
                "description":"The unique identifier for a user",
                "type":"string",
                "pattern": "^[0-9A-Za-z\_\-]+$"
            },
            "name":{
                "description":"Name of the user",
                "type":"string"
            }
        },
        "required":[
            "unique_id",
            "name"
        ]
    }
    return schema

# validate the json data from the schema
def validateJson(entityName, json_data):
    schema = get_schema(entityName)
    
    try:
        validator = jsonschema.Draft202012Validator(schema)
        errors = validator.iter_errors(json_data)
        err_list = []
        for error in errors:
            logInfo("The JSON data is not valid", error)
            err_list.append(error)
        return err_list        
    except jsonschema.exceptions.ValidationError as err:
        raise Exception(err)

