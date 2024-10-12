output "RestApiEndPoint" {
  description = "Application end point to access from public"
  value       = "https://${aws_api_gateway_rest_api.restApiGateway.id}.execute-api.${var.aws_region}.amazonaws.com/${aws_api_gateway_stage.apiStage.stage_name}/*/*"
}