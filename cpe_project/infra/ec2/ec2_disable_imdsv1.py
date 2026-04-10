"""
Ensure that a specified AWS EC2 instance uses IMDSv2.

Usage: python3 ec2_disable_imdsv1.py -p <profile> -i <instance_id> [-r <region>]
"""

import argparse
import sys

from botocore.exceptions import ClientError

from cpe_project.core.aws_client import AWSClient
from cpe_project.core.logger import get_logger

log = get_logger("EC2IMDSv2")


def ensure_imdsv2(ec2_client, instance_id: str) -> None:
    """Require IMDSv2 on the given EC2 instance."""
    try:
        ec2_client.modify_instance_metadata_options(
            InstanceId=instance_id,
            HttpTokens="required",
        )
        log.info("IMDSv2 is now required on instance %s.", instance_id)
    except ClientError as e:
        log.error("Failed: %s", AWSClient.handle_client_error(e, instance_id))
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Ensure IMDSv2 for an AWS EC2 instance."
    )
    parser.add_argument("-p", "--profile", required=True, help="AWS profile name")
    parser.add_argument("-i", "--instance", required=True, help="EC2 instance ID")
    parser.add_argument("-r", "--region", default="us-east-1", help="AWS region")
    args = parser.parse_args()

    aws = AWSClient(profile=args.profile, region=args.region)
    ec2_client = aws.client("ec2")
    ensure_imdsv2(ec2_client, args.instance)


if __name__ == "__main__":
    main()
