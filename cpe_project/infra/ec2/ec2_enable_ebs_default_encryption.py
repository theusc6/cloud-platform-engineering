"""
This script enables default EBS encryption for a specified AWS account and region.

Usage: python3 enable_ebs_default_encryption.py --profile <profile_name> --region <region_name>
"""

import argparse
import boto3
from botocore.exceptions import ClientError

def parse_args():
    """
    Parse command-line arguments passed to the script.
    """
    parser = argparse.ArgumentParser(
        description='Enable default EBS encryption for an AWS account and region.'
    )
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name')
    parser.add_argument('-r', '--region', required=True, type=str,
                        help='AWS region')
    return parser.parse_args()

def enable_ebs_encryption_by_default(ec2_client):
    """
    Enable default EBS encryption on the specified AWS account and region.

    Parameters:
    ec2_client (botocore.client.EC2): The EC2 client.
    """
    try:
        response = ec2_client.enable_ebs_encryption_by_default()
        if response['EbsEncryptionByDefault']:
            print("Success! EBS default encryption is now enabled.")
        else:
            print("EBS default encryption is not enabled.")
    except ClientError as client_error:
        print(f"An error occurred: {client_error}")

def main():
    """
    Main function of the script.
    """
    args = parse_args()
    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    ec2_client = session.client('ec2')
    enable_ebs_encryption_by_default(ec2_client)

if __name__ == "__main__":
    main()
