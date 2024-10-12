output "data_source_table_arn" {
  value = aws_dynamodb_table.data_source_table.arn
  description = "The ARN of the master data source of application DOMS"
}

output "data_source_table_name" {
  value = aws_dynamodb_table.data_source_table.id
  description = "The name of the master data source of application DOMS"
}
