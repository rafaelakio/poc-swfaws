output "swf_domain_name" {
  description = "SWF domain name"
  value       = aws_swf_domain.main.name
}

output "swf_domain_arn" {
  description = "SWF domain ARN"
  value       = aws_swf_domain.main.arn
}

output "decision_worker_function_name" {
  description = "Decision worker Lambda function name"
  value       = aws_lambda_function.decision_worker.function_name
}

output "activity_worker_function_name" {
  description = "Activity worker Lambda function name"
  value       = aws_lambda_function.activity_worker.function_name
}

output "sns_topic_arn" {
  description = "SNS topic ARN for notifications"
  value       = aws_sns_topic.workflow_notifications.arn
}
