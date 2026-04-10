"""
Enable automatic rotation for a specific AWS KMS key.

Usage: python3 kms_enable_auto_rotation.py -p <profile> -k <key_id> [-r <region>]
"""

import argparse
import sys

from botocore.exceptions import ClientError

from cpe_project.core.aws_client import AWSClient
from cpe_project.core.logger import get_logger

log = get_logger("KMSRotation")


def enable_rotation(kms_client, key_id: str) -> None:
    """Enable automatic rotation for the given KMS key."""
    try:
        kms_client.enable_key_rotation(KeyId=key_id)
        log.info("Enabled auto-rotation for KMS key '%s'.", key_id)
    except ClientError as e:
        log.error("Failed: %s", AWSClient.handle_client_error(e, key_id))
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Enable auto-rotation for an AWS KMS key."
    )
    parser.add_argument("-p", "--profile", required=True, help="AWS profile name")
    parser.add_argument("-k", "--key", required=True, help="KMS key ID")
    parser.add_argument("-r", "--region", default="us-east-1", help="AWS region")
    args = parser.parse_args()

    aws = AWSClient(profile=args.profile, region=args.region)
    kms_client = aws.client("kms")
    enable_rotation(kms_client, args.key)


if __name__ == "__main__":
    main()
