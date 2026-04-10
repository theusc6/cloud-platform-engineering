"""
This script sets encryption for a specific AWS Athena workgroup.

Usage: python3 encrypt_athena_workgroup.py --profile <profile_name> 
--workgroup <workgroup_name> 
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
        description='Set encryption for an Athena workgroup.'
    )
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('-w', '--workgroup', required=True, type=str,
                        help='Athena workgroup name')
    parser.add_argument('-r', '--region', type=str,
                        help='AWS region for the workgroup')
    return parser.parse_args()

def encrypt_athena_workgroup(athena, workgroup_name):
    """
    Set encryption for the specified Athena workgroup.
    """
    try:
        athena.update_work_group(
            WorkGroup=workgroup_name,
            ConfigurationUpdates={
                'ResultConfigurationUpdates': {
                    'EncryptionConfiguration': {
                        'EncryptionOption': 'SSE_S3',
                    }
                }
            }
        )
        print(f"Success! Set encryption for Athena workgroup '{workgroup_name}'.")
    except ClientError as client_error:
        error_message = client_error.response['Error']['Message']
        error_code = client_error.response['Error']['Code']

        if error_code == 'WorkGroupNotFoundException':
            print(f"WorkGroupNotFoundException occurred. The workgroup '{workgroup_name}' "
                  f"cannot be found. Error Message: {error_message}")

        elif error_code == "InvalidRequestException":
            print(f"InvalidRequestException occurred. The request was invalid. "
                  f"Error Message: {error_message}")

        else:
            print(f"An error occurred. Error Code: {error_code}, Error Message: {error_message}")

def main():
    """
    Main function of the script.
    """
    args = parse_args()
    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    athena = session.client('athena')

    encrypt_athena_workgroup(athena, args.workgroup)

if __name__ == "__main__":
    main()
