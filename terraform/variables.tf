# terraform/variables.tf
variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

# terraform/outputs.tf
output "guardduty_detector_id" {
  description = "The ID of the GuardDuty detector"
  value       = aws_guardduty_detector.main.id
}

output "sns_topic_arn" {
  description = "The ARN of the SNS topic for GuardDuty alerts"
  value       = aws_sns_topic.guardduty_alerts.arn
}

output "security_monitor_role_arn" {
  description = "The ARN of the IAM role for the security monitor"
  value       = aws_iam_role.security_monitor.arn
}

output "findings_archive_bucket" {
  description = "The name of the S3 bucket for findings archive"
  value       = aws_s3_bucket.findings_archive.id
}
