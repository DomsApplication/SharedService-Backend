variable "aws_region" {
    description = "AWS region"
    type = string
}

variable "stack_name" {
  description = "The stack name of the project"
  type = string
  default = "shavika"
}

variable "github_owner" {
    description = "github repository owner"
    type = string
}

variable "deploy_env" {
    description = "deployment environment"
    type = string
    default = "dev"
}

variable "deploy_repo" {
    description = "deployment github repository"
    type = string
}

variable "product" {
    description = "project name tag"
    type = string
    default = "DOMS" 
}

variable "product_version" {
  description = "product verison tag"
  type = string
  default = "1.0.0"
}

variable "customer_name" {
  description = "customer name tag"
  type = string
  default = "epd"
}

variable "revenue_type" {
    description = "revenue type tag"
    type = string
    default = "non-rev" 
}

variable "requestor_name" {
    description = "requestor name tag"
    type = string
    default = ""
}

variable "pipeline_token" {
  description = "Github token passed in from CI workflow"
  type = string
  default = ""
}

variable "function_directory" {
  description = "Github repo function path"
  type = string
  default = "."
}

## DynamoDb ###################################
variable "data_source_name" {
  type        = string
  default = "doms"
  description = "DynamoDB service name for data repository with all tenant base."
}

## lambda ###################################
variable "layer_zip_path_with_name" {
  description = "this is the path with file name of layer zip file located under core-lib"
  type = string
  default = "build/core-lib-layer.zip"
}

variable "lambda_names" {
  type    = list(string)
  description = "Using this variables creating aws lambdas, lambda roles and code archive"
  default = [
    "authentication",
    "authorization",
    "admin"
  ]
}

## api-gateway ###################################
variable "api_gateway_stage_name" {
  type        = string
  default = "v1"
  description = "Stage name for the API Gateway"
}


