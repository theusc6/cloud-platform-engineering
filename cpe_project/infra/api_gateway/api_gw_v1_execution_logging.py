"""
This script configures Execution Logging and X-Ray Tracing for AWS API Gateway Stages (REST API).

It first checks for a necessary CloudWatch Logs role, creating and/or applying one if needed.

Then, it either processes a single specified API or all APIs, enabling execution logging 
and X-Ray tracing for each stage of the API(s).

Usage: python3 api_gw_v1_execution_logging.py --profile <profile_name> -r <region> --api <api_id>
       python3 api_gw_v1_execution_logging.py --profile <profile_name> -r <region> --all
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
        description='Configure Execution Logging and X-Ray Tracing for AWS API Gateway Stages.'
        )
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('-r', '--region', default='us-west-2', type=str,
                        help='AWS region (default: us-west-2)')
    parser.add_argument('-api', '--api', type=str,
                        help='Specific REST API ID')
    parser.add_argument('-a', '--all', action='store_true',
                        help='Process all REST APIs in the account')
    return parser.parse_args()

def get_or_create_cloudwatch_log_role(session):
    """
    Get or create CloudWatch Logs role.
    """
    role_name = 'APIGatewayCloudWatchLogsRole'
    policy_arn = 'arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs'
    assume_role_policy_document = {
        'Version': '2012-10-17',
        'Statement': [{
            'Effect': 'Allow',
            'Principal': {'Service': 'apigateway.amazonaws.com'},
            'Action': 'sts:AssumeRole'
        }]
    }

    apigw = session.client('apigateway')
    iam = session.client('iam')

    try:
        account = apigw.get_account()
        if 'cloudwatchRoleArn' in account:
            print(f"Existing role is '{account['cloudwatchRoleArn']}'")
            return account['cloudwatchRoleArn']
    except ClientError as error:
        print(f"An error occurred: {error.response['Error']['Message']}")

    # If no role is assigned, create or get the specified role
    try:
        role = iam.get_role(RoleName=role_name)
        print(f"Role '{role_name}' already exists.")
        cloudwatch_logs_role_arn = role['Role']['Arn']
    except ClientError as get_role_error:
        if get_role_error.response['Error']['Code'] == 'NoSuchEntity':
            try:
                iam.create_role(
                    RoleName=role_name,
                    AssumeRolePolicyDocument=json.dumps(assume_role_policy_document)
                )
                print(f"{role_name} successfully created")
            except ClientError as create_role_error:
                print(f"An error occurred: {create_role_error.response['Error']['Message']}")
                return None

            try:
                iam.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
                print(f"Attached policy '{policy_arn}' to role '{role_name}'")
                cloudwatch_logs_role_arn = iam.get_role(RoleName=role_name)['Role']['Arn']
            except ClientError as attach_policy_error:
                print(f"An error occurred: {attach_policy_error.response['Error']['Message']}")
                return None
        else:
            print(f"An error occurred: {get_role_error.response['Error']['Message']}")
            return None


    try:
        apigw.update_account(
                patchOperations=[
                    {
                        'op': 'replace',
                        'path': '/cloudwatchRoleArn',
                        'value': cloudwatch_logs_role_arn
                    },
                ]
            )
        print(f"{role_name} successfully assigned to API Gateway for CloudWatch Logging.")
    except ClientError as error:
        print(f"An error occurred: {error.response['Error']['Message']}")
        return None


    return cloudwatch_logs_role_arn


def enable_execution_logging_and_tracing_for_stage(apigw, rest_api_id, stage_name):
    """
    Enable execution logging and X-Ray tracing for the given API Gateway REST API Stage.
    """
    try:
        apigw.update_stage(
            restApiId=rest_api_id,
            stageName=stage_name,
            patchOperations=[
                {
                    'op': 'replace',
                    'path': '/*/*/logging/dataTrace',
                    'value': 'true'
                },
                {
                    'op': 'replace',
                    'path': '/*/*/logging/loglevel',
                    'value': 'INFO'  # 'INFO' logs both 'INFO' and 'ERROR' messages
                },
                {
                    'op': 'replace',
                    'path': '/tracingEnabled',
                    'value': 'true'
                },
            ],
        )
        print(f"Execution logging and X-ray tracing has been enabled for "
              f"Stage '{stage_name}' of restApiId '{rest_api_id}'.")
    except ClientError as error:
        print(f"An error occurred: {error.response['Error']['Message']}")

def process_all_stages_of_api(session, api_id):
    """
    Loop through all the Stages of a specific REST API and
    enable execution logging and X-Ray tracing.
    """
    apigw = session.client('apigateway')
    try:
        response = apigw.get_stages(
            restApiId=api_id
        )
        for stage in response['item']:
            stage_name = stage['stageName']
            enable_execution_logging_and_tracing_for_stage(apigw, api_id, stage_name)
    except ClientError as error:
        if error.response['Error']['Code'] == 'NotFoundException':
            print(f"API with ID '{api_id}' does not exist.")
        else:
            print(f"An error occurred: {error.response['Error']['Message']}")

def process_all_rest_apis(session):
    """
    Loop through all REST APIs and their Stages and enable execution logging and X-Ray tracing.
    """
    apigw = session.client('apigateway')
    paginator = apigw.get_paginator('get_rest_apis')
    for response in paginator.paginate():
        for api in response['items']:
            rest_api_id = api['id']
            process_all_stages_of_api(session, rest_api_id)

def main():
    """
    Main function of the script.
    """
    args = parse_args()
    session = boto3.Session(profile_name=args.profile, region_name=args.region)

    if get_or_create_cloudwatch_log_role(session):
        if args.api:
            process_all_stages_of_api(session, args.api)
        elif args.all:
            process_all_rest_apis(session)
        else:
            print("Please provide either the --all option or the --api "
                  "option followed by an API ID.")
    else:
        print("Failed to get or create CloudWatch Logs role. "
              "Please check your permissions and try again.")

if __name__ == "__main__":
    main()
