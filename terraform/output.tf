output "AuthenticationFunctionName" {
  value = module.lambda.authentication_lambda_name
  description = "Authentication Lambda funcation name"
}

output "AuthorizationFunctionName" {
  value = module.lambda.authentication_lambda_name
  description = "Authorization Lambda funcation name"
}

output "AdminFunctionName" {
  value = module.lambda.admin_lambda_name
  description = "Admin Lambda funcation name"
}

output "DataSourceTableName" {
  value = module.dynamodb.data_source_table_name
  description = "DynamoDB table for serverless microserive architecture for DOMS product (Data Object Modeling)"
}

output "RestApiEndPoint" {
  value = module.api-gateway.RestApiEndPoint
  description = "Application end point to access form public"
}
