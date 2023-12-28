import jsonschema
from logger import logInfo, logDebug, logError, logException
from repository import getItemByEntityPk

# Get a JsonSchema from the dynamodb using entity name.
def get_schema(entityName):
    schema = getItemByEntityPk('SCHEMA', entityName)
    return schema

# validate the json data from the schema
def validateJson(entityName, json_data):
    try:
        schema = get_schema(entityName)
        errors = jsonschema.Draft202012Validator(schema).iter_errors(json_data)
        err_list = []
        for error in errors:
            err_list.append(errorMessage(str(error.absolute_path), error.message))
        if not err_list:     
            return True, ""        
        else:
            return False, '\n'.join(err_list)        
    except jsonschema.exceptions.ValidationError as err:
        raise Exception(err)

# Prepare the validation error message as human readable format.
def errorMessage(path, message):
    path = path.replace("deque(", "")
    path = path.replace(")", "")
    return ' : '.join([path, message])