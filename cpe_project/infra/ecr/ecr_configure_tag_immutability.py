"""
This script enables tag immutability for a specified AWS ECR repository.

Usage: python ecr_configure_tag_immutability.py
--profile <profile_name>
--repository <repository_name>
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
        description='Enable tag immutability for an AWS ECR repository.'
    )
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name')
    parser.add_argument('-r', '--repository', required=True, type=str,
                        help='ECR repository name')
    parser.add_argument('--region', type=str, default="us-west-2",
                        help='AWS region')
    return parser.parse_args()

def enable_ecr_tag_immutability(ecr_client, repository_name):
    """
    Enable tag immutability for the specified Amazon ECR repository.

    Parameters:
    ecr_client (botocore.client.ECR): The ECR client.
    repository_name (str): The name of the ECR repository.
    """
    try:
        ecr_client.put_image_tag_mutability(
            repositoryName=repository_name,
            imageTagMutability='IMMUTABLE'
        )
        print(f"Tag immutability enabled for repository: {repository_name}")
    except ClientError as client_error:
        print(f"An error occurred: {client_error}")

def main():
    """
    Main function of the script.
    """
    args = parse_args()
    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    ecr_client = session.client('ecr')
    enable_ecr_tag_immutability(ecr_client, args.repository)

if __name__ == "__main__":
    main()
