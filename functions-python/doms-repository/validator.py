import json
import jsonschema
from logger import logInfo, logDebug, logError, logException
from repository import getItemByEntityIndexPk

# https://donofden.com/blog/2020/03/15/How-to-Validate-JSON-Schema-using-Python
# https://json-schema.org/understanding-json-schema/reference/object
# https://python-jsonschema.readthedocs.io/en/stable/validate/

# Get a JsonSchema from the dynamodb using entity name.
def get_schema(entityName):
    schema = getItemByEntityIndexPk('SCHEMA', entityName)
    logInfo("get_schema/schema", schema)
    if schema is None:
        raise Exception(f"'Schema with the name '{entityName}' not exists.")
    return json.loads(schema)

# validate the json data from the entity name
def validateJsonEntityName(entityName, json_data):
    try:
        schema = get_schema(entityName)
        return validateJsonSchema(schema, json_data)
    except Exception as err:
        logException(err)        
        raise Exception(err)

# validate the json data from the schema
def validateJsonSchema(schema, json_data):
    try:
        logInfo("validateJson/json_data", json_data)
        logInfo("validateJson/schema", schema)
        errors = jsonschema.Draft202012Validator(schema).iter_errors(json_data)
        err_list = []
        for error in errors:
            err_list.append(errorMessage(str(error.absolute_path), error.message))
        if not err_list:
            return True, ""        
        else:
            return False, '\n'.join(err_list)
    except jsonschema.exceptions.ValidationError as err:
        logException(err)        
        raise Exception(err)

# Prepare the validation error message as human readable format.
def errorMessage(path, message):
    path = path.replace("deque(", "")
    path = path.replace(")", "")
    return ' : '.join([path, message])