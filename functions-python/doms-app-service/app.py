from typing import Optional

import requests
from pydantic import BaseModel, Field
from aws_lambda_powertools import Logger, Tracer

from aws_lambda_powertools.event_handler import ( APIGatewayRestResolver, Response, content_types, CORSConfig,)
from aws_lambda_powertools.event_handler.exceptions import ( BadRequestError, InternalServerError, NotFoundError,  ServiceError,  UnauthorizedError,)
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.event_handler.openapi.models import Contact, Server

import controller_user

tracer = Tracer()
logger = Logger()
base_endpoint = "/api/repo"
cors_config = CORSConfig(allow_origin="*", allow_credentials=True, allow_headers=["X-Caller-Id", "X-Signature", "X-Request-Id", "Authorization"], max_age=60000)
app = APIGatewayRestResolver(enable_validation=True, cors=cors_config)  
app.enable_swagger(path= f"{base_endpoint}/swagger")
app.include_router(controller_user.router, prefix=base_endpoint)
app.get_openapi_json_schema(title="DOMS application", version="1.0.0", description="Doms application repository service endpoints.")


@app.not_found
@tracer.capture_method
def handle_not_found_errors(exc: NotFoundError) -> Response:
    logger.info(f"Not found route: {app.current_event.path}")
    return Response(
        status_code=404, 
        content_type=content_types.APPLICATION_JSON, 
        body="{ \"message\" : \"Path not found...\"}"
        )


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)