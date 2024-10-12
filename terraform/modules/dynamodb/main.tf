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
# aws dynamodb : This is for the default data source for the application 
########################################################################
resource "aws_dynamodb_table" "data_source_table" {
  name = "${var.stack_name}-${var.data_source_name}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key  = "PK"
  range_key = "SK"

  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "SK"
    type = "S"
  }

  attribute {
    name = "ENTITIES"
    type = "S"
  }

  attribute {
    name = "PARENT"
    type = "S"
  }

  attribute {
    name = "MAPPINGS"
    type = "S"
  }

  ttl {
      attribute_name = "TIMETOLIVE"
      enabled        = true
    }

  global_secondary_index {
    name               = "ENTITIES_INX"
    hash_key           = "ENTITIES"
    range_key          = "PK"
    projection_type    = "ALL"
  }

  global_secondary_index {
    name            = "PATENT_INX"
    hash_key        = "PARENT"
    range_key       = "SK"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "MAPPINGS_IDX"
    hash_key        = "MAPPINGS"
    range_key       = "PK"
    projection_type = "ALL"
  }

  lifecycle {
    prevent_destroy = true
  }

}