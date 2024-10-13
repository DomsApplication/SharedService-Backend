####################################
# Provider
####################################
terraform {
  required_providers {
    aws = {
        source = "hashicorp/aws"
        version = "4.45.0"
    }
  }
  required_version = ">=1.5.0"
}

provider "aws" {
  alias = "acm"
  region = var.aws_region
}


########################################################################
# aws s3 bucket : This is for store files for backend application 
########################################################################
module "s3-bucket" {
  source = "./modules/s3-bucket"

  aws_region = var.aws_region
  stack_name = var.stack_name
  github_owner = var.github_owner
  deploy_env = var.deploy_env
  deploy_repo = var.deploy_repo
  product = var.product
  product_version = var.product_version
  customer_name = var.customer_name
  revenue_type = var.revenue_type
  requestor_name = var.requestor_name
  pipeline_token = var.pipeline_token

}


########################################################################
# aws dynamodb : This is for data store for backend application 
########################################################################
module "dynamodb" {
  source = "./modules/dynamodb"

  aws_region = var.aws_region
  stack_name = var.stack_name
  github_owner = var.github_owner
  deploy_env = var.deploy_env
  deploy_repo = var.deploy_repo
  product = var.product
  product_version = var.product_version
  customer_name = var.customer_name
  revenue_type = var.revenue_type
  requestor_name = var.requestor_name
  pipeline_token = var.pipeline_token

  data_source_name = var.data_source_name
}


########################################################################
# aws lambda : This is for deploy the application services 
########################################################################
module "lambda" {
  source = "./modules/lambda"

  aws_region = var.aws_region
  stack_name = var.stack_name
  github_owner = var.github_owner
  deploy_env = var.deploy_env
  deploy_repo = var.deploy_repo
  product = var.product
  product_version = var.product_version
  customer_name = var.customer_name
  revenue_type = var.revenue_type
  requestor_name = var.requestor_name
  pipeline_token = var.pipeline_token
  function_directory = var.function_directory

  backend_s3_bucket_name = module.s3-bucket.backend_bucket_name
  data_source_table_name = module.dynamodb.data_source_table_name
  layer_zip_path_with_name = var.layer_zip_path_with_name
  lambda_names = var.lambda_names
}


################################################################################
# aws api-gateway : This is for api-gateway to integrate with lambda functions 
###############################################################################
module "api-gateway" {
  source = "./modules/api-gateway"

  aws_region = var.aws_region
  stack_name = var.stack_name
  github_owner = var.github_owner
  deploy_env = var.deploy_env
  deploy_repo = var.deploy_repo
  product = var.product
  product_version = var.product_version
  customer_name = var.customer_name
  revenue_type = var.revenue_type
  requestor_name = var.requestor_name
  pipeline_token = var.pipeline_token

  api_gateway_stage_name = var.api_gateway_stage_name
  authentication_function_arn = module.lambda.authentication_lambda_arn
  authorization_function_arn = module.lambda.authorization_lambda_arn
  admin_function_arn = module.lambda.admin_lambda_arn
  
}