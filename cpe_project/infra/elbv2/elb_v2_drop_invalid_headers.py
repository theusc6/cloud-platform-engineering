"""
This script enables "drop invalid header fields" for a specific AWS
Application Load Balancer using its ID.

Usage: python3 enable_drop_invalid_header.py --profile <profile_name>
--load-balancer-id <load_balancer_id>
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
        description='Enable "drop invalid header fields" for an AWS Application Load Balancer.'
    )
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('-lb', '--load-balancer-id', required=True, type=str,
                        help='Application Load Balancer ID')
    parser.add_argument('-r', '--region', default='us-west-2', type=str,
                        help='AWS region')
    return parser.parse_args()

def get_load_balancer_arn(elbv2_client, load_balancer_id):
    """
    Get the full ARN for the given load balancer ID.
    """
    try:
        response = elbv2_client.describe_load_balancers()
        if response and 'LoadBalancers' in response:
            for load_balancer in response['LoadBalancers']:
                if load_balancer['LoadBalancerArn'].split('/')[-1] == load_balancer_id:
                    return load_balancer['LoadBalancerArn']
    except ClientError as client_error:
        print(f"Error fetching ARN for Load Balancer ID {load_balancer_id}: {client_error}")

    return None

def enable_drop_invalid_header(elbv2_client, load_balancer_arn):
    """
    Enable "drop invalid header fields" for the specified AWS Application Load Balancer.
    """
    try:
        response = elbv2_client.modify_load_balancer_attributes(
            LoadBalancerArn=load_balancer_arn,
            Attributes=[
                {
                    'Key': 'routing.http.drop_invalid_header_fields.enabled',
                    'Value': 'true'
                }
            ]
        )

        if response and response.get('Attributes'):
            for attr in response['Attributes']:
                if (attr['Key'] == 'routing.http.drop_invalid_header_fields.enabled'
                    and attr['Value'] == 'true'):
                    print(f"Successfully enabled 'drop invalid header fields' "
                          f"for Load Balancer '{load_balancer_arn}'.")
                    return
            print(f"Failed to enable 'drop invalid header fields' "
                  f"for Load Balancer '{load_balancer_arn}'.")

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

    elbv2_client = session.client('elbv2')

    load_balancer_arn = get_load_balancer_arn(elbv2_client, args.load_balancer_id)
    if not load_balancer_arn:
        print(f"Failed to fetch ARN for Load Balancer ID '{args.load_balancer_id}'.")
        return

    enable_drop_invalid_header(elbv2_client, load_balancer_arn)

if __name__ == "__main__":
    main()
