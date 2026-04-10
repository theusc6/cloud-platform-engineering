"""
Stitch Integration Deployment Script
"""

import argparse
import json
import boto3

def create_iam_role_and_policy(args):
    """
    Create IAM role and policy in AWS
    """
    # Initialize a Boto3 IAM client using the provided AWS profile
    session = boto3.Session(profile_name=args.aws_profile)
    iam_client = session.client('iam')

    # Define the trust policy document with external account and external ID
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": f"arn:aws:iam::{args.external_account_number}:root"
                },
                "Action": "sts:AssumeRole",
                "Condition": {
                    "StringEquals": {
                        "sts:ExternalId": args.external_id
                    }
                }
            }
        ]
    }

    # Create the IAM role with the trust policy and add a "Name" tag
    iam_client.create_role(
        RoleName=args.role_name,
        AssumeRolePolicyDocument=json.dumps(trust_policy),
        Tags=[{'Key': 'Name', 'Value': 'Stitch'}]
    )


    # Create the IAM policy and add a "Name" tag
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "dynamodb:ListTables",
                    "dynamodb:DescribeStream",
                    "dynamodb:ListStreams",
                    "dynamodb:DescribeTable",
                    "dynamodb:GetRecords",
                    "dynamodb:Scan",
                    "dynamodb:GetShardIterator"
                ],
                "Resource": ["*"]
            }
        ]
    }

    policy_response = iam_client.create_policy(
        PolicyName=args.policy_name,
        PolicyDocument=json.dumps(policy_document),
        Tags=[{'Key': 'Name', 'Value': 'Stitch'}]
    )

    # Attach the policy to the IAM role
    policy_arn = policy_response['Policy']['Arn']
    iam_client.attach_role_policy(
        RoleName=args.role_name,
        PolicyArn=policy_arn
    )

def main():
    """
    Main function
    """

    parser = argparse.ArgumentParser(description="Create IAM role and policy in AWS")
    parser.add_argument("--role-name", required=True, help="Name for the IAM role")
    parser.add_argument("--external-account-number", required=True,
                        help="External AWS account number")
    parser.add_argument("--external-id", required=True, help="External ID for trust policy")
    parser.add_argument("--policy-name", required=True, help="Name for the IAM policy")
    parser.add_argument("--aws-profile", required=True, help="AWS profile to use")

    args = parser.parse_args()

    create_iam_role_and_policy(args)

if __name__ == "__main__":
    main()
