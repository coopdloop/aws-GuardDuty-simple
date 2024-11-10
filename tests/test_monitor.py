# tests/test_monitor.py
import pytest
from security_monitor.monitor import CloudSecurityMonitor
import boto3
from botocore.exceptions import ClientError


def test_guardduty_setup():
    monitor = CloudSecurityMonitor()
    detector_id = monitor.setup_guardduty()
    assert detector_id is not None


def test_sns_topic_creation():
    monitor = CloudSecurityMonitor()
    topic_arn = monitor.create_sns_topic()
    assert topic_arn is not None
