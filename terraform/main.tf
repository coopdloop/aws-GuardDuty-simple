# terraform/main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Uncomment and configure if you want to use remote state
  # backend "s3" {
  #   bucket = "your-terraform-state-bucket"
  #   key    = "security-monitor/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      Project     = "SecurityMonitor"
      ManagedBy   = "Terraform"
    }
  }
}

# GuardDuty Detector
resource "aws_guardduty_detector" "main" {
  enable = true

  datasources {
    s3_logs {
      enable = true
    }
    kubernetes {
      audit_logs {
        enable = true
      }
    }
  }
}

# SNS Topic for GuardDuty Alerts
resource "aws_sns_topic" "guardduty_alerts" {
  name = "guardduty-alerts"
}

# IAM Role for the Python application
resource "aws_iam_role" "security_monitor" {
  name = "security-monitor-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com" # Modify if using different service
        }
      }
    ]
  })
}

# IAM Policy for the security monitor
resource "aws_iam_role_policy" "security_monitor" {
  name = "security-monitor-policy"
  role = aws_iam_role.security_monitor.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "guardduty:GetDetector",
          "guardduty:GetFindings",
          "guardduty:ListFindings",
          "guardduty:UpdateDetector",
          "sns:Publish",
          "sns:ListTopics"
        ]
        Resource = [
          aws_guardduty_detector.main.arn,
          aws_sns_topic.guardduty_alerts.arn,
          "${aws_sns_topic.guardduty_alerts.arn}/*"
        ]
      }
    ]
  })
}

# EventBridge Rule for GuardDuty Findings
resource "aws_cloudwatch_event_rule" "guardduty_findings" {
  name        = "capture-guardduty-findings"
  description = "Capture all GuardDuty findings"

  event_pattern = jsonencode({
    source      = ["aws.guardduty"]
    detail-type = ["GuardDuty Finding"]
  })
}

# EventBridge Target - Send findings to SNS
resource "aws_cloudwatch_event_target" "sns" {
  rule      = aws_cloudwatch_event_rule.guardduty_findings.name
  target_id = "SendToSNS"
  arn       = aws_sns_topic.guardduty_alerts.arn

  input_transformer {
    input_paths = {
      title       = "$.detail.title"
      description = "$.detail.description"
      severity    = "$.detail.severity"
      account     = "$.detail.accountId"
      region      = "$.region"
      finding     = "$.detail.id"
    }

    input_template = jsonencode(<<EOT
GuardDuty Finding in <region>:
Title: <title>
Severity: <severity>
Description: <description>
Account ID: <account>
Finding ID: <finding>
EOT
    )
  }
}

# Add SNS Topic Policy to allow EventBridge
resource "aws_sns_topic_policy" "default" {
  arn = aws_sns_topic.guardduty_alerts.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowEventBridgePublish"
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
        Action   = "SNS:Publish"
        Resource = aws_sns_topic.guardduty_alerts.arn
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          }
          ArnLike = {
            "aws:SourceArn" = aws_cloudwatch_event_rule.guardduty_findings.arn
          }
        }
      }
    ]
  })
}

# S3 Bucket for findings archive (optional)
resource "aws_s3_bucket" "findings_archive" {
  bucket = "guardduty-findings-archive-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_versioning" "findings_archive" {
  bucket = aws_s3_bucket.findings_archive.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "findings_archive" {
  bucket = aws_s3_bucket.findings_archive.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Get current AWS account ID
data "aws_caller_identity" "current" {}
