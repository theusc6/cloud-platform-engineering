"""
This script enables delivery status logging for Amazon SNS topics.

Usage: python3 enable_logging_sns.py --profile <profile_name>
--topic-arn <sns_topic_arn>
--role-arn <iam_role_arn>
--region <region_name>
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
        description='Enable delivery status logging for Amazon SNS topics.'
    )
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('-t', '--topic-name', required=True, type=str,
                        help='SNS topic ARN')
    parser.add_argument('-r', '--region', default="us-west-2", type=str,
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

    role_name = 'role-myorg-sns-logging+prod-ops'
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": [
                        "sns.amazonaws.com"
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
            'arn:aws:iam::aws:policy/service-role/AmazonSNSRole',
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

def enable_sns_delivery_status_logging(sns_client, region, account_id, topic_name, role_arn):
    """
    Enable delivery status logging for the specified Amazon SNS topic.
    """
    topic_arn=f"arn:aws:sns:{region}:{account_id}:{topic_name}"

    try:
        # The default is all logging is enabled. This can be changed according to what is
        # needed for logging needs.
        attributes_to_set = {
            'ApplicationSuccessFeedbackRoleArn': role_arn,
            'ApplicationFailureFeedbackRoleArn': role_arn,
            'ApplicationSuccessFeedbackSampleRate': '50',
            'LambdaSuccessFeedbackRoleArn': role_arn,
            'LambdaFailureFeedbackRoleArn': role_arn,
            'LambdaSuccessFeedbackSampleRate': '50',
            'HTTPSuccessFeedbackRoleArn': role_arn,
            'HTTPFailureFeedbackRoleArn': role_arn,
            'HTTPSuccessFeedbackSampleRate': '50',
            'FirehoseSuccessFeedbackRoleArn': role_arn,
            'FirehoseFailureFeedbackRoleArn': role_arn,
            'FirehoseSuccessFeedbackSampleRate': '50',
            'SQSSuccessFeedbackRoleArn' : role_arn,
            'SQSFailureFeedbackRoleArn' : role_arn,
            'SQSSuccessFeedbackSampleRate' : '50'

        }
        for attribute_name, attribute_value in attributes_to_set.items():
            sns_client.set_topic_attributes(
                TopicArn=topic_arn,
                AttributeName=attribute_name,
                AttributeValue=attribute_value
            )

        print(f"Success! Enabled delivery status logging for SNS topic '{topic_arn}'.")

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
    account_id = session.client('sts').get_caller_identity().get('Account')
    sns_client = session.client('sns')
    role_arn = create_iam_role(session)
    enable_sns_delivery_status_logging(sns_client, args.region, account_id,
                                       args.topic_name, role_arn)

if __name__ == "__main__":
    main()
