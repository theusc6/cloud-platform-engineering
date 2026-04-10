#!/usr/bin/env python3

"""
Create the required DevOps CICD pipeline role in AWS.
"""

import sys
import argparse
import boto3
from botocore.exceptions import ClientError

# Ensure a profile argument is passed in
parser = argparse.ArgumentParser(description='Create required DevOps CICD pipeline role in AWS.')
parser.add_argument('-p', '--profile', required=True, type=str,
                    help='AWS profile name for SSO login')
args = parser.parse_args()

# Set up boto3 client
session = boto3.Session(profile_name=args.profile)
iam_client = session.client('iam')

# Create the IAM role
try:
    role = iam_client.create_role(
        RoleName='devops-github-service-role',
        AssumeRolePolicyDocument={
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": [
                            "arn:aws:iam::123456789012:role/Terraform_github_actions",
                            "arn:aws:iam::123456789012:role/Terraform_github"
                        ]
                    },
                    "Action": "sts:AssumeRole",
                    "Condition": {}
                }
            ]
        }
    )

except ClientError as error:
    print(error)
    sys.exit(1)

# Attach the AWSCodePipeline role policy to the role
try:
    iam_client.attach_role_policy(
        RoleName='devops-github-service-role',
        PolicyArn='arn:aws:iam::aws:policy/AWSCodePipelineRole'
    )
except ClientError as error:
    print(error)
    sys.exit(1)

# Add required tags to the role
try:
    tags = [
        {
            'Key': 'Category',
            'Value': 'DevOps'
        },
        {
            'Key': 'Product',
            'Value': 'Pipeline'
        }
    ]
    iam_client.tag_role(
        RoleName='github-pipeline',
        Tags=tags
    )

except ClientError as error:
    print(error)
    sys.exit(1)

# Print the role ARN
print(role['Role']['Arn'])
