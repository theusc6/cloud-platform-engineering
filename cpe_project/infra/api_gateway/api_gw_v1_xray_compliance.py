"""
This script enables X-Ray tracing for AWS API Gateway Stages. 

It can either enable X-Ray tracing for all stages of a specified Rest API,
or it can process all Rest APIs in the AWS account and enable X-Ray tracing for their stages.

The script uses the AWS SDK for Python (Boto3) to interact with the AWS API Gateway service.
Command-line arguments are used to specify the AWS profile for SSO login, 
the AWS region, and whether a specific Rest API ID or all APIs should be processed.

Example usage:

To enable X-Ray tracing for all stages of a specific Rest API:
python api_gw_xray_compliance.py -p my_profile -r us-west-2 --api my_api_id

To enable X-Ray tracing for all Rest APIs in the account:
python api_gw_xray_compliance.py -p my_profile -r us-west-2 --all

This script should be used as part of a larger process to ensure
AWS API Gateway security compliance.
"""

import argparse
import boto3
from botocore.exceptions import ClientError

def parse_args():
    """
    Parse command-line arguments passed to the script.

    The script accepts the following arguments:
    - AWS profile name for SSO login (required)
    - AWS region (optional, default is 'us-west-2')
    - Specific Rest API ID (optional)
    - Option to process all APIs in the account (optional)

    Returns:
        argparse.Namespace: An object that holds attribute values for all parsed arguments.
    """
    parser = argparse.ArgumentParser(description='Enable X-Ray tracing for AWS API Gateway Stages.')
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('-r', '--region', default='us-west-2', type=str,
                        help='AWS region (default: us-west-2)')
    parser.add_argument('--api', type=str,
                        help='Specific Rest API ID')
    parser.add_argument('--all', action='store_true',
                        help='Process all APIs in the account')
    return parser.parse_args()

def enable_xray_tracing(apigw_client, rest_api_id, stage_name):
    """
    Enable X-Ray tracing for the given API Gateway Stage.
    """
    try:
        apigw_client.update_stage(
            restApiId=rest_api_id,
            stageName=stage_name,
            patchOperations=[{
                'op': 'replace',
                'path': '/tracingEnabled',
                'value': 'true'
            }]
        )
        print(f"X-Ray tracing has been enabled for Stage '{stage_name}' "
              f"of RestApiId '{rest_api_id}'.")
    except ClientError as error:
        print(f"An error occurred: {error.response['Error']['Message']}")

def process_all_stages_of_api(apigw_client, rest_api_id):
    """
    Loop through all the Stages of a specific Rest API and enable X-Ray tracing.
    """
    stages_response = apigw_client.get_stages(restApiId=rest_api_id)
    for stage in stages_response['item']:
        stage_name = stage['stageName']
        enable_xray_tracing(apigw_client, rest_api_id, stage_name)

def process_all_rest_apis(apigw_client):
    """
    Loop through all the API Gateway APIs and their Stages and enable X-Ray tracing.
    """
    paginator = apigw_client.get_paginator('get_rest_apis')
    for response in paginator.paginate():
        for api in response['items']:
            rest_api_id = api['id']
            process_all_stages_of_api(apigw_client, rest_api_id)

def main():
    """
    Main function of the script.

    Based on the command-line arguments, either process all stages
    of a specific API Gateway Rest API,
    or process all Rest APIs and their stages in the account.
    In both cases, X-Ray tracing is enabled.
    """
    args = parse_args()
    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    apigw_client = session.client('apigateway')

    if args.api:
        process_all_stages_of_api(apigw_client, args.api)
    elif args.all:
        process_all_rest_apis(apigw_client)
    else:
        print("Please provide either the --all option or the --api option followed by an API ID.")

if __name__ == "__main__":
    main()
