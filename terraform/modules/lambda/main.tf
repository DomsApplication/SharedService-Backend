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
# aws lambda layer: This is for provision the application core-library
########################################################################
resource "aws_lambda_layer_version" "python_libs" {
  layer_name = "${var.stack_name}-core-lib"
  description         = "Dependencies for the blank-python sample app."
  filename            = "${var.function_directory}/core-lib/${var.layer_zip_path_with_name}"
  compatible_architectures = [ "arm64" ]
  compatible_runtimes = ["python3.12"]
}

#######################################################################################
# aws iam role : This is for provision the application services role
#######################################################################################
resource "aws_iam_role" "lambda_roles" {
  for_each = toset(var.lambda_names)
  name = "${var.stack_name}-${each.key}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

#######################################################################################
# aws iam policy: This is for provision the application services policy
#######################################################################################
resource "aws_iam_policy" "lambda_basic_execution_policy" {
  name = "LambdaBasicExecution"
  description = "Lambda  policy added for basic execution needed"

   policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "CreateLogGroup"
        Effect   = "Allow"
        Action   = ["logs:CreateLogGroup"]
        Resource = "*"
      },
      {
        Sid      = "WriteLogStreamsAndGroups"
        Effect   = "Allow"
        Action   = ["logs:CreateLogStream", "logs:PutLogEvents"]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_dynamodb_policy" {
  name = "LambdaDynamoDBAccess"
  description = "allowing lambda to access the dynamodb & Index"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid      = "DynamoDBAccess"
      Effect   = "Allow"
      Action   = [
        "dynamodb:BatchGetItem",
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:BatchWriteItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:GetRecords"
      ]
      Resource = [
        "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/${var.data_source_table_name}",
        "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/${var.data_source_table_name}/index/*"
      ]
    }]
  })
}

resource "aws_iam_policy" "lambda_s3_bucket_policy" {
  name = "LambdaS3BucketAccess"
  description = "allowing lambda to access the s3 bucket to store & retrive the files"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid      = "S3BucketAccess"
      Effect   = "Allow"
      Action   = [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket",
        "s3:GetObjectVersion",
        "s3:PutObjectAcl",
        "s3:PutLifecycleConfiguration",
        "s3:GetLifecycleConfiguration",
        "s3:DeleteObject",
        "s3:GetBucketLocation"
      ]
      Resource = [
        "arn:aws:s3:::${var.backend_s3_bucket_name}",
        "arn:aws:s3:::${var.backend_s3_bucket_name}/*"
      ]
    }]
  })
}

########################################################################
# aws iam role & policy attachment: attach the policy to roles
########################################################################
resource "aws_iam_role_policy_attachment" "lambda_role_policy_attachment_for_basic_execution" {
  for_each = toset(var.lambda_names)

  role       = aws_iam_role.lambda_roles[each.key].name
  policy_arn = aws_iam_policy.lambda_basic_execution_policy.arn
}

resource "aws_iam_role_policy_attachment" "lambda_role_policy_attachment_for_dynamodb" {
  for_each = toset(var.lambda_names)

  role       = aws_iam_role.lambda_roles[each.key].name
  policy_arn = aws_iam_policy.lambda_dynamodb_policy.arn
}

resource "aws_iam_role_policy_attachment" "lambda_role_policy_attachment_for_s3_bucket" {
  for_each = toset(var.lambda_names)

  role       = aws_iam_role.lambda_roles[each.key].name
  policy_arn = aws_iam_policy.lambda_s3_bucket_policy.arn
}

########################################################################
# aws lambda zip: This will generate a zip file for each lambda finction.
########################################################################
data "archive_file" "lambda_code" {
  for_each = toset(var.lambda_names)

  type        = "zip"
  source_dir  = "${var.function_directory}/${each.key}"  # Path to your function code
  output_file_mode = "0666"
  output_path = "${var.function_directory}/${each.key}/${each.key}.zip"  # Zip output location
}

########################################################################
# aws lambda functions: This is for provision the application services
########################################################################
resource "aws_lambda_function" "lambda_functions" {
  for_each = toset(var.lambda_names)
  
  function_name = "${var.stack_name}-${each.key}-lambda"

  handler       = "app.lambda_handler"
  runtime       = "python3.12"
  memory_size   = 128
  timeout       = 25
  architectures = ["arm64"]
  tracing_config {
    mode = "Active"
  }
  
  layers = [aws_lambda_layer_version.python_libs.arn]
  role = aws_iam_role.lambda_roles[each.key].arn

  filename      = "${var.function_directory}/${each.key}/${each.key}.zip"
  source_code_hash = filebase64sha256("${var.function_directory}/${each.key}/${each.key}.zip")

  environment {
    variables = {
      POWERTOOLS_LOG_LEVEL        = "INFO"
      POWERTOOLS_LOGGER_SAMPLE_RATE = "0.1"
      POWERTOOLS_LOGGER_LOG_EVENT = "true"
      POWERTOOLS_SERVICE_NAME     = var.product
      AWS_Region                  = var.aws_region
      AWS_AccountId               = data.aws_caller_identity.current.account_id
      DDB_TABLE_NAME              = var.data_source_table_name
      S3_BUCKET_NAME              = var.backend_s3_bucket_name
    }
  }
}