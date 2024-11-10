# src/main.py
from security_monitor.monitor import CloudSecurityMonitor
import logging
import json


def main():
    # Initialize the security monitor
    monitor = CloudSecurityMonitor()

    try:
        # Setup GuardDuty
        detector_id = monitor.setup_guardduty()
        print(f"GuardDuty detector ID: {detector_id}")

        # Create SNS topic
        topic_arn = monitor.create_sns_topic()
        print(f"SNS topic ARN: {topic_arn}")

        # List any findings
        findings = monitor.list_findings(detector_id)
        print("Current findings:")
        print(json.dumps(findings, indent=2))

    except Exception as e:
        logging.error(f"Error in security monitor setup: {e}")
        raise


if __name__ == "__main__":
    main()
