"""
This script enables enhanced image scanning on all ECR private
repositories for a specified AWS account and region.

Usage: python3 enable_ecr_enhanced_image_scanning.py
--profile <profile_name>
--region <region_name>
"""

import argparse
import boto3
from botocore.exceptions import ClientError

def parse_args():
    """
    Parse command-line arguments passed to the script.
    """
    parser = argparse.ArgumentParser(
        description='Enable enhanced image scanning on all ECR private'
        'repositories for an AWS account and region.'
    )
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name')
    parser.add_argument('-r', '--region', required=True, type=str,
                        help='AWS region')
    return parser.parse_args()

def enable_image_scanning(ecr_client):
    """
    Enable enhanced image scanning on all ECR repositories.

    Parameters:
    ecr_client (botocore.client.ECR): The ECR client.
    """
    try:
        ecr_client.put_registry_scanning_configuration(
            scanType='ENHANCED',
            rules=[
                {
                    'scanFrequency': 'CONTINUOUS_SCAN',
                    'repositoryFilters': [
                        {
                            'filter': '*',
                            'filterType': 'WILDCARD'
                        },
                    ]
                },
            ]
        )
        print("Success! Enabled enhanced & continuous image scanning.")
    except ClientError as client_error:
        print(f"An error occurred: {client_error}")

def main():
    """
    Main function of the script.
    """
    args = parse_args()
    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    ecr_client = session.client('ecr', region_name=args.region)

    enable_image_scanning(ecr_client)

if __name__ == "__main__":
    main()
