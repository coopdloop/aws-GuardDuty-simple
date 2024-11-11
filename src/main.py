# src/main.py
from security_monitor.monitor import CloudSecurityMonitor
import logging
import json


def main():
    # Initialize the security monitor
    monitor = CloudSecurityMonitor()

    try:
        # Setup or get existing GuardDuty detector
        detector_id = monitor.get_or_create_detector()
        print(f"GuardDuty detector ID: {detector_id}")

        # Get detector status
        status = monitor.get_detector_status(detector_id)
        print("\nDetector Status:")
        print(json.dumps(status, indent=2))

        # Create or get SNS topic
        topic_arn = monitor.create_sns_topic()
        print(f"\nSNS topic ARN: {topic_arn}")

        # List any findings
        findings = monitor.list_findings(detector_id)
        print("\nCurrent findings:")
        if findings:
            print(json.dumps(findings, indent=2))
        else:
            print("No findings found")

    except Exception as e:
        logging.error(f"Error in security monitor setup: {e}")
        raise


if __name__ == "__main__":
    main()
