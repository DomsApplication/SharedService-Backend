#output "lambda_function_arns" {
  #description = "ARNs of all Lambda functions"
  #value       = { for lambda_name, lambda in aws_lambda_function.lambda_functions : lambda_name => lambda.arn }
#}

output "authentication_lambda_arn" {
  value = aws_lambda_function.lambda_functions["authentication"].arn
}

output "authentication_lambda_name" {
  value = aws_lambda_function.lambda_functions["authentication"].id
}

output "authorization_lambda_arn" {
  value = aws_lambda_function.lambda_functions["authorization"].arn
}

output "authorization_lambda_name" {
  value = aws_lambda_function.lambda_functions["authorization"].id
}

output "admin_lambda_arn" {
  value = aws_lambda_function.lambda_functions["admin"].arn
}

output "admin_lambda_name" {
  value = aws_lambda_function.lambda_functions["admin"].id
}