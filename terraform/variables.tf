variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "poc-swfaws"
}

variable "swf_domain_name" {
  description = "SWF domain name"
  type        = string
  default     = "business-process-domain"
}

variable "swf_task_list" {
  description = "SWF task list name"
  type        = string
  default     = "business-process-tasks"
}

variable "retention_days" {
  description = "Workflow execution retention period in days"
  type        = number
  default     = 30
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default = {
    Project     = "poc-swfaws"
    Environment = "dev"
    ManagedBy   = "Terraform"
  }
}
