from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import ( APIGatewayRestResolver, Response, content_types, CORSConfig,)
from aws_lambda_powertools.event_handler.exceptions import ( BadRequestError, InternalServerError, NotFoundError,  ServiceError,  UnauthorizedError,)
from aws_lambda_powertools.event_handler.openapi.exceptions import RequestValidationError
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

import controller_user
import DomsException

tracer = Tracer()
logger = Logger()
base_endpoint = "/api/repo"

cors_config = CORSConfig(allow_origin="*", allow_credentials=True, allow_headers=["X-Caller-Id", "X-Signature", "X-Request-Id", "Authorization"], max_age=60000)
app = APIGatewayRestResolver(enable_validation=True, cors=cors_config)  
app.enable_swagger(path= "/api/docs/swagger")
app.include_router(controller_user.router, prefix=base_endpoint)
app.get_openapi_json_schema(title="DOMS application", version="1.0.0", description="Doms application repository service endpoints.")


@app.not_found
@tracer.capture_method
def handle_not_found_errors(exc: NotFoundError) -> Response:
    logger.info(f"Not found route: {app.current_event.path}")
    return sendResponse(404, { "message" : f"Not found route: {app.current_event.path}"})

@app.exception_handler(RequestValidationError)  
def handle_validation_error(ex: RequestValidationError):
    logger.error("Request failed validation", path=app.current_event.path, errors=ex.errors())
    return sendResponse(422, { "message" : "Invalid data"})

def sendResponse(code, body):
    return Response(
        status_code=code, 
        content_type=content_types.APPLICATION_JSON, 
        body= body
        )


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)