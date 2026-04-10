"""
AWS IAM Management Script

This script automates the creation of IAM policies and roles in AWS for S3 & Stitch integration. 
It allows users to create a new IAM policy and role with specific permissions and tags
and then attaches the policy to the role. This is particularly useful for managing S3 
bucket access in different environments and for different Stitch accounts.

The script uses Boto3, the AWS SDK for Python, and requires AWS credentials
configured for the target account.

Arguments:
    --profile: AWS profile name for SSO login.
    --bucket_name: Name of the S3 bucket to access.
    --stitch_account_id: Stitch Account ID for integration.
    --stitch_external_id: Stitch External ID for integration.
    --environment: Environment type (e.g., dev, prod, uat, etc.).
    --owner: JIRA/ServiceNow ticket number for tracking.
    --ticket_number: Owner of the resource or ticket requestor.
    --role_name: Name for the new IAM role.

Usage:
    python aws_iam_script.py --profile <profile_name> --bucket_name <bucket_name> 
    --stitch_account_id <stitch_account_id> --stitch_external_id <stitch_external_id>
    --environment <environment> --owner <owner> --ticket_number <ticket_number> 
    --role_name <role_name>    
"""

import time
import json
import argparse
import boto3

from botocore.exceptions import ClientError

def create_iam_policy(iam_client, policy_name, policy_document, role_tags):
    """
    Creates the IAM policy.
    """
    try:
        response = iam_client.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document),
            Tags=role_tags
        )
        time.sleep(60)
        print("Created policy: policy_name")
        return response['Policy']['Arn']

    except ClientError as error:
        print(f"Error creating IAM policy: {error}")
        return None

def create_iam_role(iam_client, role_name, trust_policy, policy_arn, role_tags):
    """
    Creates the IAM role and attaches the policy.
    """
    try:
        iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Tags=role_tags
        )
        print(f"Created role: {role_name}")

        time.sleep(60)
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_arn
        )
        print("Successfully attached the policy to the role.")
        print("All line items complete.")
    except ClientError as error:
        print(f"Error creating IAM role: {error}")

def main():
    """
    Main function to perform all operations.
    """
    parser = argparse.ArgumentParser(description="AWS S3 & Stitch Integration Script")
    parser.add_argument('--profile', '-p', required=True, help='AWS profile name for SSO login')
    parser.add_argument('--bucket_name', required=True, help="Name of the S3 bucket")
    parser.add_argument('--stitch_account_id', required=True, help="Stitch Account ID")
    parser.add_argument('--stitch_external_id', required=True, help="Stitch External ID")
    parser.add_argument('--environment', required=True,
                         help="Environment Type (dev,prod,uat,etc.)")
    parser.add_argument('--owner', required=True, help="JIRA/ServiceNow ticket number")
    parser.add_argument('--ticket_number', required=True, help="Owner of resource/ticket requestor")

    parser.add_argument('--role_name', required=True, help="stitch_xx_xx")
    args = parser.parse_args()

    role_tags = [
    {"Key": "Ticket Number", "Value": f"{args.ticket_number}"},
    {"Key": "Owner", "Value": f"{args.owner}"},
    ]

    session = boto3.Session(profile_name=args.profile)
    iam_client = session.client('iam')

    # Policy document
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "",
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:ListBucket"],
                "Resource": [
                    f"arn:aws:s3:::{args.bucket_name}",
                    f"arn:aws:s3:::{args.bucket_name}/*"
                ]
            }
        ]
    }

    policy_name = f"policy-myorg-stitch-s3-{args.bucket_name}-integration+{args.environment}-ops"
    policy_arn = create_iam_policy(iam_client, policy_name, policy_document, role_tags)

    # Trust policy for IAM role
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": f"arn:aws:iam::{args.stitch_account_id}:root"},
                "Action": "sts:AssumeRole",
                "Condition": {
                    "StringEquals": {
                        "sts:ExternalId": f"{args.stitch_external_id}"
                    }
                }
            }
        ]
    }

    create_iam_role(iam_client, args.role_name, trust_policy, policy_arn, role_tags)

if __name__ == "__main__":
    main()
