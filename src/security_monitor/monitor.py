# src/security_monitor/monitor.py
import boto3
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get Terraform outputs
with open("terraform/terraform.tfstate") as f:
    state = json.load(f)
    outputs = state["outputs"]

# detector_id = outputs["guardduty_detector_id"]["value"]
sns_topic_arn = outputs["sns_topic_arn"]["value"]


class CloudSecurityMonitor:
    def __init__(self, region_name="us-east-1"):
        self.region_name = region_name
        self.guardduty = boto3.client("guardduty", region_name=region_name)
        self.securityhub = boto3.client("securityhub", region_name=region_name)
        self.sns = boto3.client("sns", region_name=region_name)

    def get_or_create_detector(self):
        """Get existing detector or create a new one"""
        try:
            # List existing detectors
            detectors = self.guardduty.list_detectors()

            if detectors["DetectorIds"]:
                # detector_id = detectors["DetectorIds"][0]
                detector_id = outputs["guardduty_detector_id"]["value"]
                logger.info(f"Using existing GuardDuty detector: {detector_id}")

                # Update existing detector
                self.guardduty.update_detector(
                    DetectorId=detector_id,
                    Enable=True,
                    DataSources={
                        "S3Logs": {"Enable": True},
                        "Kubernetes": {"AuditLogs": {"Enable": True}},
                    },
                )
                return detector_id

            # Create new detector if none exists
            response = self.guardduty.create_detector(
                Enable=True,
                DataSources={
                    "S3Logs": {"Enable": True},
                    "Kubernetes": {"AuditLogs": {"Enable": True}},
                },
                Tags={"Environment": "Production", "Project": "SecurityMonitor"},
            )
            detector_id = response["DetectorId"]
            logger.info(f"Created new GuardDuty detector: {detector_id}")
            return detector_id

        except Exception as e:
            logger.error(f"Error managing GuardDuty detector: {e}")
            raise

    def get_detector_status(self, detector_id):
        """Get the status of a GuardDuty detector"""
        try:
            response = self.guardduty.get_detector(DetectorId=detector_id)
            return {
                "status": "enabled" if response["Status"] == "ENABLED" else "disabled",
                "data_sources": response.get("DataSources", {}),
                "service_role": response.get("ServiceRole", ""),
                "updated_at": response.get("UpdatedAt", ""),
            }
        except Exception as e:
            logger.error(f"Error getting detector status: {e}")
            raise

    def create_sns_topic(self):
        """Create or get SNS topic for alerts"""
        try:
            # Check if topic already exists
            topics = self.sns.list_topics()
            existing_topic = next(
                (
                    topic
                    for topic in topics["Topics"]
                    if "GuardDutyAlerts" in topic["TopicArn"]
                ),
                None,
            )

            if existing_topic:
                logger.info(f"Using existing SNS topic: {existing_topic['TopicArn']}")
                return existing_topic["TopicArn"]

            # Create new topic if none exists
            response = self.sns.create_topic(Name="GuardDutyAlerts")
            topic_arn = response["TopicArn"]
            logger.info(f"Created new SNS topic: {topic_arn}")
            return topic_arn

        except Exception as e:
            logger.error(f"Error managing SNS topic: {e}")
            raise

    def list_findings(self, detector_id, max_results=10):
        """List GuardDuty findings"""
        try:
            response = self.guardduty.list_findings(
                DetectorId=detector_id,
                SortCriteria={"AttributeName": "severity", "OrderBy": "DESC"},
                MaxResults=max_results,
            )

            if not response["FindingIds"]:
                logger.info("No findings found")
                return []

            findings = self.guardduty.get_findings(
                DetectorId=detector_id, FindingIds=response["FindingIds"]
            )

            return findings["Findings"]

        except Exception as e:
            logger.error(f"Error listing findings: {e}")
            raise
