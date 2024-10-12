####################################
# Provider
####################################
terraform {
  required_providers {
    aws = {
        source = "hashicorp/aws"
        version = "4.45.0"
    }
    github = {  
        source = "hashicorp/github"
        version = "~> 6.3.0" # Check for the latest version
    }
  }
  required_version = ">=1.5.0"
}

provider "aws" {
  alias = "acm"
  region = var.aws_region
  default_tags {
    tags = {
      env = var.deploy_env
      product = var.product
      productversion = var.product_version
      customer = var.customer_name
      revenue = var.revenue_type
      requestor = var.requestor_name
      managedby = "Terraform"
    }
  }
}

provider "github" {
  token = var.pipeline_token
  owner = var.github_owner
}

########################################################################
# data: Fetch AWS account ID using aws_caller_identity
########################################################################
data "aws_caller_identity" "current" {}

########################################################################
# aws api-gateway RestApi: api-gateway for lambda integration
########################################################################
resource "aws_api_gateway_rest_api" "restApiGateway" {
  name        = "${var.stack_name}-discover-registry"
  description = "An API Gateway with a Lambda Integration"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_deployment" "apiDeployment" {
  depends_on = [
    aws_api_gateway_method.authMethod,
    aws_api_gateway_method.adminMethod,
    aws_api_gateway_method.adminSwaggerMethod
  ]

  rest_api_id = aws_api_gateway_rest_api.restApiGateway.id
  description = "Deploy the auth rest API"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "apiStage" {
  deployment_id = aws_api_gateway_deployment.apiDeployment.id
  rest_api_id   = aws_api_gateway_rest_api.restApiGateway.id
  stage_name    = var.api_gateway_stage_name
  description   = "Staging the auth rest API"
}

############################################################################################
# aws api-gateway lambda Authorizer: api-gateway authorization using custom lambda function
############################################################################################
resource "aws_api_gateway_authorizer" "AuthorizersLambdaToken" {
  name   = "LambdaAuthorizerToken"
  type   = "TOKEN"
  rest_api_id              = aws_api_gateway_rest_api.restApiGateway.id
  identity_source          = "method.request.header.Authorization"
  authorizer_result_ttl_in_seconds = 300

  authorizer_uri = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${var.authorization_function_arn}/invocations"
}

resource "  " "tokenAuthzLambdaApiGatewayInvoke" {
  action        = "lambda:InvokeFunction"
  function_name = var.authorization_function_arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.aws_region}:${data.aws_caller_identity.current.account_id}:${aws_api_gateway_rest_api.restApiGateway.id}/authorizers/${aws_api_gateway_authorizer.AuthorizersLambdaToken.id}"
}

############################################################################################
# aws api-gateway resource: RESOURCE PATH "/api/auth/{proxy+}"
############################################################################################
resource "aws_api_gateway_resource" "apiResource" {
  parent_id = aws_api_gateway_rest_api.restApiGateway.root_resource_id
  path_part = "api"
  rest_api_id = aws_api_gateway_rest_api.restApiGateway.id
}

resource "aws_api_gateway_resource" "authResource" {
  parent_id = aws_api_gateway_resource.apiResource.id
  path_part = "auth"
  rest_api_id = aws_api_gateway_rest_api.restApiGateway.id
}

resource "aws_api_gateway_resource" "authProxyResource" {
  parent_id = aws_api_gateway_resource.authResource.id
  path_part = "{proxy+}"
  rest_api_id = aws_api_gateway_rest_api.restApiGateway.id
}

# <<<<<<< resource => /api/auth/{proxy+} | method {ANY} |  lambda-proxy-integration >>>>>>>>>>>
resource "aws_api_gateway_method" "authMethod" {
  rest_api_id   = aws_api_gateway_rest_api.restApiGateway.id
  resource_id   = aws_api_gateway_resource.authProxyResource.id
  authorization = "NONE"
  http_method   = "ANY"
  operation_name = "auth lambda function"
}

resource "aws_api_gateway_integration" "authIntegration" {
  rest_api_id   = aws_api_gateway_rest_api.restApiGateway.id
  resource_id   = aws_api_gateway_resource.authProxyResource.id
  http_method   = aws_api_gateway_method.authMethod.http_method
  
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${var.authentication_function_arn}/invocations"
  passthrough_behavior    = "WHEN_NO_MATCH"
  timeout_milliseconds     = 29000 
}

# <<<<<<< Auth lambda API-execution-permissions for rest-api >>>>>>>>>>>
resource "aws_lambda_permission" "authLambdaApiGatewayInvoke" {
  action        = "lambda:InvokeFunction"
  function_name = var.authentication_function_arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.aws_region}:${data.aws_caller_identity.current.account_id}:${aws_api_gateway_rest_api.restApiGateway.id}/${var.api_gateway_stage_name}/ANY/api/auth/{proxy+}"
}

############################################################################################
# aws api-gateway resource: RESOURCE PATH "/api/admin/"
############################################################################################
resource "aws_api_gateway_resource" "adminResource" {
  parent_id = aws_api_gateway_resource.apiResource.id
  path_part = "admin"
  rest_api_id = aws_api_gateway_rest_api.restApiGateway.id
}

resource "aws_api_gateway_resource" "adminProxyResource" {
  parent_id = aws_api_gateway_resource.adminResource.id
  path_part = "{proxy+}"
  rest_api_id = aws_api_gateway_rest_api.restApiGateway.id
}

# <<<<<<< resource => /api/admin/{proxy+} | method {ANY} |  lambda-proxy-integration >>>>>>>>>>>
resource "aws_api_gateway_method" "adminMethod" {
  authorization  = "CUSTOM"
  authorizer_id  = aws_api_gateway_authorizer.AuthorizersLambdaToken.id
  http_method    = "ANY"
  resource_id    = aws_api_gateway_resource.adminProxyResource.id
  rest_api_id    = aws_api_gateway_rest_api.restApiGateway.id

  operation_name = "Database repository operation with lambda function"
}

resource "aws_api_gateway_integration" "adminIntegration" {
  rest_api_id   = aws_api_gateway_rest_api.restApiGateway.id
  resource_id   = aws_api_gateway_resource.adminProxyResource.id
  http_method   = aws_api_gateway_method.adminMethod.http_method
  
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${var.admin_function_arn}/invocations"
  passthrough_behavior    = "WHEN_NO_MATCH"
  timeout_milliseconds     = 29000 
}

# <<<<<<< Admin lambda API-execution-permissions for rest-api >>>>>>>>>>>
resource "aws_lambda_permission" "adminLambdaApiGatewayInvoke" {
  action        = "lambda:InvokeFunction"
  function_name = var.admin_function_arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.aws_region}:${data.aws_caller_identity.current.account_id}:${aws_api_gateway_rest_api.restApiGateway.id}/${var.api_gateway_stage_name}/ANY/api/admin/{proxy+}"
}

