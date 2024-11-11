# AWS GuardDuty Security Monitor

A comprehensive AWS security monitoring solution using GuardDuty, deployed with Terraform and managed with Python.

## Architecture

This solution deploys:
- AWS GuardDuty Detector
- SNS Topic for alerts
- EventBridge rules for automated notifications
- IAM roles and policies
- S3 bucket for findings archive
- CloudWatch metrics and alarms
- Optional email notifications

## Prerequisites

- AWS Account with appropriate permissions
- Terraform (>= 1.0)
- Python 3.8 or higher
- AWS CLI configured
- Git

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/coopdloop/aws-GuardDuty-simple
cd aws-security-monitor
```

2. Initialize Terraform:
```bash
cd terraform
terraform init
```

3. Configure variables (optional):
```bash
# Create terraform.tfvars
cat << EOF > terraform.tfvars
aws_region = "us-east-1"
environment = "production"
alert_email = "your.email@example.com"  # Optional
EOF
```

4. Deploy infrastructure:
```bash
terraform plan
terraform apply
```

5. Set up Python environment:
```bash
cd ..
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -e .
```

## Directory Structure

```
aws-security-monitor/
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── terraform.tfvars
├── src/
│   └── security_monitor/
│       ├── __init__.py
│       └── monitor.py
├── tests/
│   └── test_monitor.py
└── README.md
```

## Terraform Resources

The following resources are created:
- GuardDuty Detector with S3 and Kubernetes monitoring
- SNS Topic for alerts
- EventBridge rules for finding notifications
- IAM role and policies
- S3 bucket for findings archive
- CloudWatch metric alarms

## Python Monitoring Tool

The Python tool provides:
- GuardDuty findings monitoring
- Custom finding filters
- Automated notifications
- Findings archival

## Usage

### 1. Deploy Infrastructure

```bash
cd terraform
terraform apply
```

### 2. Monitor Findings

```bash
python src/main.py
```

### 3. Generate Test Findings

```bash
# Get detector ID
DETECTOR_ID=$(terraform output -raw guardduty_detector_id)

# Create sample finding
aws guardduty create-sample-findings \
    --detector-id $DETECTOR_ID \
    --finding-types "Recon:EC2/PortProbeUnprotectedPort"
```

## Configuration Options

### Terraform Variables

| Variable | Description | Default |
|----------|-------------|---------|
| aws_region | AWS Region | us-east-1 |
| environment | Environment name | production |
| alert_email | Email for notifications | "" |

### Python Configuration

Update `.env` file:
```bash
AWS_REGION=us-east-1
ENVIRONMENT=production
```

## Monitoring and Alerts

1. Email Notifications:
- Set `alert_email` in terraform.tfvars
- Confirm subscription in your email

2. CloudWatch Metrics:
- High severity findings alarm
- Finding count metrics
- Custom metric dashboards

## Cleanup

To remove all created resources:

1. Destroy Terraform resources:
```bash
cd terraform
terraform destroy
```

2. Clean up Python environment:
```bash
deactivate
cd ..
rm -rf venv
```

## Security Considerations

1. IAM Permissions:
- Least privilege access
- Resource-level permissions
- Service control policies

2. Data Protection:
- S3 bucket encryption
- SNS topic encryption
- CloudWatch logs encryption

3. Monitoring:
- Regular finding review
- Alert configuration
- Audit logging

## Troubleshooting

### Common Issues

1. **Terraform Apply Fails**
```bash
# Check AWS credentials
aws sts get-caller-identity

# Validate Terraform files
terraform validate
```

2. **GuardDuty Findings Not Appearing**
```bash
# Check detector status
aws guardduty list-detectors
aws guardduty get-detector --detector-id $DETECTOR_ID
```

3. **SNS Notifications Not Working**
```bash
# Verify SNS topic
aws sns list-topics
aws sns list-subscriptions
```

## Development

### Adding New Features

1. Terraform:
```bash
# Create new branch
git checkout -b feature/new-feature

# Make changes and test
terraform plan
```

2. Python:
```bash
# Update code
pip install -e .
pytest tests/
```

## Best Practices

1. Infrastructure:
- Use version controlled Terraform state
- Implement proper tagging
- Enable encryption

2. Monitoring:
- Regular findings review
- Alert thresholds adjustment
- Response plan documentation

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and feature requests:
1. Check existing issues
2. Create new issue with:
   - Clear description
   - Steps to reproduce
   - Expected behavior

## References

- [AWS GuardDuty Documentation](https://docs.aws.amazon.com/guardduty/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Security Best Practices](https://aws.amazon.com/architecture/security-identity-compliance/)
