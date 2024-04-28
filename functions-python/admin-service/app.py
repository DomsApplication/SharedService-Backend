import requests

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import ( APIGatewayRestResolver, Response, CORSConfig)
from aws_lambda_powertools.event_handler.exceptions import ( BadRequestError, InternalServerError, NotFoundError,  ServiceError,  UnauthorizedError)
from aws_lambda_powertools.event_handler.openapi.exceptions import RequestValidationError
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from utlities import sendResponse
import controller_dataobject
import controller_datarepository

tracer = Tracer()
logger = Logger()

base_endpoint = "/api/admin"
cors_config = CORSConfig(
    allow_origin="*", 
    allow_credentials=True,
    allow_headers=["Content-Type", "Content-Disposition", "Accept", "Authorization", "x-xsrf-tokens", "access-control-max-age", "origin"], 
    expose_headers=["Content-Type", "Content-Disposition", "Accept", "Authorization", "x-xsrf-tokens"],
    max_age=1800000)
app = APIGatewayRestResolver(enable_validation = True, cors = cors_config)    
#app = APIGatewayRestResolver(enable_validation = True)    
app.enable_swagger(path= f"{base_endpoint}/swagger")
app.include_router(controller_dataobject.router, prefix=base_endpoint)
app.include_router(controller_datarepository.router, prefix=base_endpoint)
app.get_openapi_json_schema(title="DOMS application", version="1.0.0", description="Doms application repository service endpoints.")


@app.not_found
@tracer.capture_method
def handle_not_found_errors(exc: NotFoundError) -> Response:
    logger.info(f"Not found route: {app.current_event.path}")
    return sendResponse(404, { "message" : "Path not found..."})

@app.exception_handler(RequestValidationError)  
def handle_validation_error(ex: RequestValidationError):
    logger.error("Request failed validation", path=app.current_event.path, errors=ex.errors())
    return sendResponse(422, { "error" : ex.errors()})

# You can continue to use other utilities just as before
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
