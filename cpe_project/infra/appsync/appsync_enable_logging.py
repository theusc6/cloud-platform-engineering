"""
This script enables CloudWatch Logs logging for a specific AWS AppSync API.

Usage: python3 enable_logging_appsync_api.py --profile <profile_name>
--api <api_id>
--region <region_name>
--logrole <log_role_arn>
"""

import argparse
import json
import time
import boto3

from botocore.exceptions import ClientError

def parse_args():
    """
    Parse command-line arguments passed to the script.
    """
    parser = argparse.ArgumentParser(
        description='Enable CloudWatch Logs logging for an AWS AppSync API.'
    )
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('-a', '--api', required=True, type=str,
                        help='AppSync API ID')
    parser.add_argument('-r', '--region', type=str, default="us-west-2",
                        help='AWS region')
    return parser.parse_args()

def create_iam_role(session):
    """
    Creates an IAM role with specific policies and returns its ARN.

    Parameters:
    session (boto3.Session): An AWS session object created by Boto3.

    Returns:
    str: The ARN of the created IAM role.
    """
    iam_client = session.client('iam')

    role_name = 'role-myorg-appsync-logging+prod-ops'
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": [
                        "appsync.amazonaws.com"
                    ]
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }

    try:
        create_role_response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for AppSync to push logs to CloudWatch',
            Tags=[
                {
                    'Key': 'Category',
                    'Value': 'Security'
                }
            ]
        )

        policy_arns = [
            'arn:aws:iam::aws:policy/service-role/AWSAppSyncPushToCloudWatchLogs',
        ]

        for policy_arn in policy_arns:
            iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn
            )
        print(f"Creating {role_name}...")
        time.sleep(10)
        print(f"The role {role_name} successfully created.")
        return create_role_response['Role']['Arn']


    except ClientError as client_error:
        if client_error.response['Error']['Code'] == 'EntityAlreadyExists':
            print(f"The IAM role {role_name} already exists.")
            role_arn = iam_client.get_role(RoleName=role_name)['Role']['Arn']
            return role_arn

        print(f"An error occurred while creating the IAM role: "
            f"{client_error.response['Error']['Message']}")
        return None

def enable_logging_for_appsync_api(appsync_client, api_id, role_arn):
    """
    Enable CloudWatch Logs logging for the specified AWS AppSync API.
    """
    try:
        # Fetching the current name of the GraphQL API
        current_api = appsync_client.get_graphql_api(apiId=api_id)
        api_name = current_api['graphqlApi']['name']

        # Using the fetched name to update the API's logging settings
        appsync_client.update_graphql_api(
            apiId=api_id,
            authenticationType='API_KEY',
            name=api_name,  # Passing the fetched name here
            logConfig={
                'fieldLogLevel': 'ALL',  # Options: NONE, ERROR, ALL
                'cloudWatchLogsRoleArn': role_arn
            }
        )
        print(f"Success! Enabled CloudWatch Logs logging for AppSync API '{api_id}'.")
    except ClientError as client_error:
        error_message = client_error.response['Error']['Message']
        error_code = client_error.response['Error']['Code']
        print(f"An error occurred. Error Code: {error_code}, Error Message: {error_message}")

def main():
    """
    Main function of the script.
    """
    args = parse_args()
    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    appsync_client = session.client('appsync')
    role_arn = create_iam_role(session)
    enable_logging_for_appsync_api(appsync_client, args.api, role_arn)

if __name__ == "__main__":
    main()
