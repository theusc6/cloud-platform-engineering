"""
This script sets the retention period of CloudWatch Logs to 1 year.
This is the minimum requirement as set forth by CloudWatch.16.
The rule fails if the retention period is not at least 1 year.

Usage: python3 set_cloudwatch_logs_retention.py --profile <profile_name>
--log-group-name <log_group_name>
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
        description='Set retention period of CloudWatch Logs to 1 year.'
    )
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('-l', '--log-group-name', required=True, type=str,
                        help='The name of the log group to modify')
    parser.add_argument('-r', '--region', type=str,
                        help='AWS region for CloudWatch Logs')
    return parser.parse_args()

def set_cloudwatch_logs_retention(cloudwatch_logs, log_group_name):
    """
    Set retention period for the specified CloudWatch Log Group.
    """
    try:
        cloudwatch_logs.put_retention_policy(
            logGroupName=log_group_name,
            retentionInDays=365
        )
        print(f"Success! Set retention period for CloudWatch Log "
              f"Group '{log_group_name}' to 1 year.")
    except ClientError as client_error:
        error_message = client_error.response['Error']['Message']
        error_code = client_error.response['Error']['Code']

        if error_code == 'ResourceNotFoundException':
            print(f"ResourceNotFoundException occurred. The log group '{log_group_name}' "
                  f"cannot be found. Error Message: {error_message}")
        elif error_code == "InvalidParameterException":
            print(f"InvalidParameterException occurred. The request had invalid parameters. "
                  f"Error Message: {error_message}")
        else:
            print(f"An error occurred. Error Code: {error_code}, Error Message: {error_message}")

def main():
    """
    Main function of the script.
    """
    args = parse_args()
    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    cloudwatch_logs = session.client('logs')

    set_cloudwatch_logs_retention(cloudwatch_logs, args.log_group_name)

if __name__ == "__main__":
    main()
