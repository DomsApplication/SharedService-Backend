import json
import jsonschema
from aws_lambda_powertools import Logger, Tracer
import DomsException

tracer = Tracer()
logger = Logger()

# https://donofden.com/blog/2020/03/15/How-to-Validate-JSON-Schema-using-Python
# https://json-schema.org/understanding-json-schema/reference/object
# https://python-jsonschema.readthedocs.io/en/stable/validate/

# Get unique Id from the given entity schema
@tracer.capture_method
def getUniqueIdFromSchema(entitySchema):
    if 'version' not in entitySchema:
        raise DomsException(400, {'error' : f"'version' field is missed in Schema {entitySchema['entity']}."})
    elif 'uniquekey' not in entitySchema['properties']['entity']:
        raise DomsException(400, {'error' : f"'entity.uniquekey' field is missed in Schema {entitySchema['entity']}."})
    else:
        return entitySchema['properties']['entity']['uniquekey']

# validate the json data from the schema
@tracer.capture_method
def validateRequestBodyWithDataObject(schema, data):
    try:
        logger.info("validateJson/json_data", data)
        logger.info("validateJson/schema", schema)
        errors = jsonschema.Draft202012Validator(schema).iter_errors(data)
        err_list = []
        for error in errors:
            err_list.append(errorMessage(str(error.absolute_path), error.message))
        if not err_list:
            return True, ""        
        else:
            return False, '\n'.join(err_list)
    except jsonschema.exceptions.ValidationError as err:
        logger.error(err)        
        raise Exception(err)

# Prepare the validation error message as human readable format.
@tracer.capture_method
def errorMessage(path, message):
    path = path.replace("deque(", "")
    path = path.replace(")", "")
    return ' : '.join([path, message])

# Get a list of fields which is True of searchable.
@tracer.capture_method
def getSearchFields(_entitySchema, payload):
    searchableList = []
    # Loop along dictionary keys
    for field_key in _entitySchema['properties']:
        field = _entitySchema['properties'][field_key]
        if  field['searchable'] is not None and field['searchable'] is True:
            ply_key = field_key
            ply_type = field['type']
            ply_value = payload[field_key]
            item = {}
            item[ply_key] = ply_value
            item['type'] = ply_type
            searchableList.append(item)
    return searchableList

# List the field which is required in the schema
#https://stackoverflow.com/questions/31750725/get-required-fields-from-json-schema
@tracer.capture_method
def required_dict(schema):
    return {
        key: key in schema['required']
        for key in schema['properties']
    }