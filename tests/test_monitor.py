# tests/test_monitor.py
import pytest
from security_monitor.monitor import CloudSecurityMonitor
import boto3
from botocore.exceptions import ClientError


@pytest.fixture
def monitor():
    """Create a CloudSecurityMonitor instance for testing"""
    return CloudSecurityMonitor()


def test_guardduty_setup(monitor):
    """Test GuardDuty detector creation"""
    try:
        detector_id = monitor.setup_guardduty()
        assert detector_id is not None
    except ClientError as e:
        if e.response["Error"]["Code"] == "AccessDeniedException":
            pytest.skip("AWS credentials don't have sufficient permissions")
        raise


def test_sns_topic_creation(monitor):
    """Test SNS topic creation"""
    try:
        topic_arn = monitor.create_sns_topic()
        assert topic_arn is not None
        assert topic_arn.startswith("arn:aws:sns:")
    except ClientError as e:
        if e.response["Error"]["Code"] == "AccessDeniedException":
            pytest.skip("AWS credentials don't have sufficient permissions")
        raise


@pytest.fixture(autouse=True)
def aws_credentials():
    """Ensure AWS credentials are available"""
    try:
        boto3.client("sts").get_caller_identity()
    except Exception as e:
        pytest.skip(f"AWS credentials not configured: {str(e)}")
