# Terraform para POC SWF AWS
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# SWF Domain
resource "aws_swf_domain" "main" {
  name                                        = var.swf_domain_name
  description                                 = "SWF domain for ${var.project_name}"
  workflow_execution_retention_period_in_days = var.retention_days

  tags = var.tags
}

# IAM Role for Lambda (Workers)
resource "aws_iam_role" "lambda_execution" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

# IAM Policy for SWF Access
resource "aws_iam_role_policy" "lambda_swf" {
  name = "${var.project_name}-swf-policy"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "swf:*"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "decision_worker" {
  name              = "/aws/lambda/${var.project_name}-decision-worker"
  retention_in_days = 7

  tags = var.tags
}

resource "aws_cloudwatch_log_group" "activity_worker" {
  name              = "/aws/lambda/${var.project_name}-activity-worker"
  retention_in_days = 7

  tags = var.tags
}

# Lambda Layer for dependencies (boto3)
resource "aws_lambda_layer_version" "dependencies" {
  filename            = "lambda_layer.zip"
  layer_name          = "${var.project_name}-dependencies"
  compatible_runtimes = ["python3.11", "python3.10", "python3.9"]
  description         = "Python dependencies for SWF workers"

  # Note: You need to create lambda_layer.zip with boto3 and other dependencies
}

# Lambda Function - Decision Worker
resource "aws_lambda_function" "decision_worker" {
  filename         = "decision_worker.zip"
  function_name    = "${var.project_name}-decision-worker"
  role             = aws_iam_role.lambda_execution.arn
  handler          = "decision_worker.lambda_handler"
  source_code_hash = filebase64sha256("decision_worker.zip")
  runtime          = "python3.11"
  timeout          = 300
  memory_size      = 512

  environment {
    variables = {
      SWF_DOMAIN    = aws_swf_domain.main.name
      SWF_TASK_LIST = var.swf_task_list
      AWS_REGION    = var.aws_region
    }
  }

  layers = [aws_lambda_layer_version.dependencies.arn]

  tags = var.tags
}

# Lambda Function - Activity Worker
resource "aws_lambda_function" "activity_worker" {
  filename         = "activity_worker.zip"
  function_name    = "${var.project_name}-activity-worker"
  role             = aws_iam_role.lambda_execution.arn
  handler          = "activity_worker.lambda_handler"
  source_code_hash = filebase64sha256("activity_worker.zip")
  runtime          = "python3.11"
  timeout          = 300
  memory_size      = 512

  environment {
    variables = {
      SWF_DOMAIN    = aws_swf_domain.main.name
      SWF_TASK_LIST = var.swf_task_list
      AWS_REGION    = var.aws_region
    }
  }

  layers = [aws_lambda_layer_version.dependencies.arn]

  tags = var.tags
}

# EventBridge Rule to trigger workers periodically
resource "aws_cloudwatch_event_rule" "decision_worker_trigger" {
  name                = "${var.project_name}-decision-worker-trigger"
  description         = "Trigger decision worker every minute"
  schedule_expression = "rate(1 minute)"

  tags = var.tags
}

resource "aws_cloudwatch_event_target" "decision_worker" {
  rule      = aws_cloudwatch_event_rule.decision_worker_trigger.name
  target_id = "DecisionWorkerLambda"
  arn       = aws_lambda_function.decision_worker.arn
}

resource "aws_lambda_permission" "allow_eventbridge_decision" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.decision_worker.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.decision_worker_trigger.arn
}

resource "aws_cloudwatch_event_rule" "activity_worker_trigger" {
  name                = "${var.project_name}-activity-worker-trigger"
  description         = "Trigger activity worker every minute"
  schedule_expression = "rate(1 minute)"

  tags = var.tags
}

resource "aws_cloudwatch_event_target" "activity_worker" {
  rule      = aws_cloudwatch_event_rule.activity_worker_trigger.name
  target_id = "ActivityWorkerLambda"
  arn       = aws_lambda_function.activity_worker.arn
}

resource "aws_lambda_permission" "allow_eventbridge_activity" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.activity_worker.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.activity_worker_trigger.arn
}

# SNS Topic for notifications
resource "aws_sns_topic" "workflow_notifications" {
  name = "${var.project_name}-notifications"

  tags = var.tags
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "decision_worker_errors" {
  alarm_name          = "${var.project_name}-decision-worker-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "This metric monitors decision worker errors"
  alarm_actions       = [aws_sns_topic.workflow_notifications.arn]

  dimensions = {
    FunctionName = aws_lambda_function.decision_worker.function_name
  }

  tags = var.tags
}
