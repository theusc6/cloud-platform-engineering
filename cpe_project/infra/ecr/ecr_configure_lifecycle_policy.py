"""
This script sets an ECR lifecycle policy with specified conditions.

Usage: python3 ecr_configure_lifecycle_policy.py
--profile <profile_name>
--repository <repository_name>
--region <region_name>
"""

import argparse
import json
import boto3

from botocore.exceptions import ClientError

def parse_args():
    """
    Parse command-line arguments passed to the script.
    """
    parser = argparse.ArgumentParser(
        description='Set ECR lifecycle policy for a specified repository.'
    )
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name')
    parser.add_argument('-r', '--repository', required=True, type=str,
                        help='ECR repository name')
    parser.add_argument('--region', type=str, default="us-west-2",
                        help='AWS region')
    return parser.parse_args()

def set_ecr_lifecycle_policy(ecr_client, repository_name):
    """
    Sets the lifecycle policy for the specified Amazon ECR repository.

    Parameters:
    ecr_client (botocore.client.ECR): The ECR client.
    repository_name (str): The name of the ECR repository.
    """
    lifecycle_policy_text = json.dumps({
        "rules": [
            {
                "rulePriority": 1,
                "description": "SecurityHub[ECR3] Default ECR Lifecycle Policy",
                "selection": {
                    "tagStatus": "any",
                    "countType": "imageCountMoreThan",
                    "countNumber": 5
                },
                "action": {
                    "type": "expire"
                }
            }
        ]
    })

    try:
        ecr_client.put_lifecycle_policy(
            repositoryName=repository_name,
            lifecyclePolicyText=lifecycle_policy_text
        )
        print(f"Lifecycle policy successfully set for repository: {repository_name}.")
    except ClientError as client_error:
        print(f"An error occurred: {client_error}")

def main():
    """
    Main function of the script.
    """
    args = parse_args()
    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    ecr_client = session.client('ecr')
    set_ecr_lifecycle_policy(ecr_client, args.repository)

if __name__ == "__main__":
    main()
