"""
This script enables publishing of usage metrics to CloudWatch for a specific
AWS Athena workgroup across multiple regions.

Usage: python3 enable_cloudwatch_metrics.py --profile <profile_name> 
--workgroup <workgroup_name> 
--regions <region1,region2,...>
"""

import argparse
import boto3
from botocore.exceptions import ClientError

def parse_args():
    """
    Parse command-line arguments passed to the script.
    """
    parser = argparse.ArgumentParser(
        description='Enable CloudWatch metrics publishing for an Athena '
        'workgroup across multiple regions.'
    )
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('-w', '--workgroup', required=True, type=str,
                        help='Athena workgroup name')
    parser.add_argument('-r', '--regions', required=True, type=str,
                        help='Comma-separated list of AWS regions for the workgroup '
                        '(e.g., us-west-1,us-west-2)')
    return parser.parse_args()

def enable_cloudwatch_metrics(athena, workgroup_name, region):
    """
    Enable CloudWatch metrics publishing for the specified Athena workgroup in a given region.
    """
    try:
        athena.update_work_group(
            WorkGroup=workgroup_name,
            ConfigurationUpdates={
                'PublishCloudWatchMetricsEnabled': True
            }
        )
        print(f"Success! Enabled CloudWatch metrics publishing for Athena workgroup "
              f"'{workgroup_name}' in region '{region}'.")
    except ClientError as client_error:
        error_message = client_error.response['Error']['Message']
        error_code = client_error.response['Error']['Code']

        if error_code == 'WorkGroupNotFoundException':
            print(f"WorkGroupNotFoundException occurred in region '{region}'. The "
                  f"workgroup '{workgroup_name}' cannot be found. Error Message: {error_message}")

        elif error_code == "InvalidRequestException":
            print(f"InvalidRequestException occurred in region '{region}'. "
                  f"The request was invalid. "
                  f"Error Message: {error_message}")

        else:
            print(f"An error occurred in region '{region}'. Error "
                  f"Code: {error_code}, Error Message: {error_message}")

def main():
    """
    Main function of the script.
    """
    args = parse_args()
    regions = args.regions.split(',')

    for region in regions:
        session = boto3.Session(profile_name=args.profile, region_name=region)
        athena = session.client('athena')
        enable_cloudwatch_metrics(athena, args.workgroup, region)

if __name__ == "__main__":
    main()
