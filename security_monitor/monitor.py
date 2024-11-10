# src/security_monitor/monitor.py
import boto3
import json
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CloudSecurityMonitor:
    def __init__(self, region_name="us-east-1"):
        self.region_name = region_name
        self.guardduty = boto3.client("guardduty", region_name=region_name)
        self.securityhub = boto3.client("securityhub", region_name=region_name)
        self.sns = boto3.client("sns", region_name=region_name)

    def setup_guardduty(self):
        """Setup and enable GuardDuty"""
        try:
            # Create GuardDuty detector
            response = self.guardduty.create_detector(
                Enable=True,
                DataSources={
                    "S3Logs": {"Enable": True},
                    "Kubernetes": {"AuditLogs": {"Enable": True}},
                },
                Tags={"Environment": "Production", "Project": "SecurityMonitor"},
            )
            detector_id = response["DetectorId"]
            logger.info(f"GuardDuty detector created: {detector_id}")
            return detector_id

        except self.guardduty.exceptions.BadRequestException as e:
            logger.error(f"Error creating GuardDuty detector: {e}")
            raise

    def create_sns_topic(self):
        """Create SNS topic for alerts"""
        try:
            response = self.sns.create_topic(Name="GuardDutyAlerts")
            topic_arn = response["TopicArn"]
            logger.info(f"SNS topic created: {topic_arn}")
            return topic_arn

        except Exception as e:
            logger.error(f"Error creating SNS topic: {e}")
            raise

    def list_findings(self, detector_id):
        """List GuardDuty findings"""
        try:
            response = self.guardduty.list_findings(
                DetectorId=detector_id,
                SortCriteria={"AttributeName": "severity", "OrderBy": "DESC"},
            )

            findings = self.guardduty.get_findings(
                DetectorId=detector_id, FindingIds=response["FindingIds"]
            )

            return findings["Findings"]

        except Exception as e:
            logger.error(f"Error listing findings: {e}")
            raise
