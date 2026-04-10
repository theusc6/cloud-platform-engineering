"""
This module is used to configure access logging for AWS API Gateway v2 stages.

You can specify the AWS profile name for SSO login, the AWS region (with a default of us-west-2),
a specific HTTP API ID, or you can choose to process all HTTP APIs in the account.

After parsing the arguments, it creates a new session using the specified profile and region.
Then it determines whether to process a single API or all APIs based on the input arguments.

If a specific API ID is provided, it enables access logging for all stages of that API.
If the --all argument is provided, it enables access logging for all stages of all
HTTP APIs in the account.

A CloudWatch log group is created for each stage, and the log group is tagged with
'Category: Security'.
The access log format is JSON.

Usage: python3 api_gw_v2_configure_access_logging.py --profile <profile_name> --api <api_id>
       python3 api_gw_v2_configure_access_logging.py --profile <profile_name> --all
"""
import argparse
import re
import boto3

from botocore.exceptions import ClientError

def parse_args():
    """
    Parse command-line arguments passed to the script.
    """
    parser = argparse.ArgumentParser(
        description='Configure Access Logging for AWS API Gateway v2 Stages.'
        )
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('-r', '--region', default='us-west-2', type=str,
                        help='AWS region (default: us-west-2)')
    parser.add_argument('-api', '--api', type=str,
                        help='Specific HTTP API ID')
    parser.add_argument('-a', '--all', action='store_true',
                        help='Process all HTTP APIs in the account')
    return parser.parse_args()

def create_log_group(cloudwatch, log_group_name):
    """
    Create a new CloudWatch log group.
    """
    try:
        cloudwatch.create_log_group(logGroupName=log_group_name)
    except ClientError as error:
        if error.response['Error']['Code'] == 'ResourceAlreadyExistsException':
            print(f"Log group {log_group_name} already exists.")
        else:
            print(f"An error occurred: {error.response['Error']['Message']}")
            return None

    try:
        response = cloudwatch.describe_log_groups(logGroupNamePrefix=log_group_name)
        log_groups = response['logGroups']
        log_group = log_groups[0]
        log_group_arn = log_group['arn']

        cloudwatch.tag_log_group(
            logGroupName=log_group_name,
            tags={
                'Category': 'Security'
            }
        )

        print(f"Log Group ARN: {log_group_arn}")  # Print the log group ARN
        return log_group_arn

    except ClientError as error:
        print(f"An error occurred: {error.response['Error']['Message']}")
        return None


def enable_access_logging(cloudwatch, apigw_v2_client, api_id, stage_name):
    """
    Enable access logging for the given API Gateway v2 Stage.
    """

    # Replace non-alphanumeric characters with a hyphen
    valid_stage_name = re.sub('[^a-zA-Z0-9]', '-', stage_name)
    log_group_name = f'/aws/apigateway/{api_id}/{valid_stage_name}'
    log_group_arn = create_log_group(cloudwatch, log_group_name)
    if log_group_arn is not None:  # Only update stage if a valid log group ARN is returned
        try:
            apigw_v2_client.update_stage(
                ApiId=api_id,
                StageName=stage_name,
                AccessLogSettings={
                    'DestinationArn': log_group_arn,
                    'Format': (
                        '{ '
                        '"requestId":"$context.requestId", '
                        '"ip": "$context.identity.sourceIp", '
                        '"caller":"$context.identity.caller", '
                        '"user":"$context.identity.user",'
                        '"requestTime":"$context.requestTime", '
                        '"httpMethod":"$context.httpMethod",'
                        '"resourcePath":"$context.resourcePath", '
                        '"status":"$context.status",'
                        '"protocol":"$context.protocol", '
                        '"responseLength":"$context.responseLength" '
                        '}'
                    )
                }
            )
            print(f"Access logging has been enabled for Stage '{stage_name}' of ApiId '{api_id}'.")
        except ClientError as error:
            print(f"An error occurred: {error.response['Error']['Message']}")
    else:
        print(f"Could not create log group for Stage '{stage_name}' of ApiId '{api_id}'.")


def process_all_stages_of_api(cloudwatch, apigw_v2_client, api_id):
    """
    Loop through all the Stages of a specific HTTP API and enable access logging.
    """
    try:
        response = apigw_v2_client.get_stages(ApiId=api_id)
        for stage in response['Items']:
            stage_name = stage['StageName']
            enable_access_logging(cloudwatch, apigw_v2_client, api_id, stage_name)
    except ClientError as error:
        print(f"An error occurred: {error.response['Error']['Message']}")

def process_all_http_apis(cloudwatch, apigw_v2_client):
    """
    Loop through all the HTTP APIs and their Stages and enable access logging.
    """
    try:
        paginator = apigw_v2_client.get_paginator('get_apis')
        for response in paginator.paginate():
            for api in response['Items']:
                api_id = api['ApiId']
                process_all_stages_of_api(cloudwatch, apigw_v2_client, api_id)
    except ClientError as error:
        print(f"An error occurred: {error.response['Error']['Message']}")

def main():
    """
    Main function of the script.
    """
    args = parse_args()
    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    apigw_v2_client = session.client('apigatewayv2')
    cloudwatch = session.client('logs')

    if args.api:
        process_all_stages_of_api(cloudwatch, apigw_v2_client, args.api)
    elif args.all:
        process_all_http_apis(cloudwatch, apigw_v2_client)
    else:
        print("Please provide either the --all option or the --api option followed by an API ID.")

if __name__ == "__main__":
    main()
