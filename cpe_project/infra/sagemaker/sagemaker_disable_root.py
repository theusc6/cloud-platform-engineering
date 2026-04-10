"""
This script disables root access for a specific Amazon SageMaker notebook instance.

Usage: python3 disable_root_access.py -p <profile_name> -r <region_name> -i <notebook_instance_name>
"""
import argparse
import boto3
from botocore.exceptions import ClientError

def parse_args():
    """
    Parse command-line arguments passed to the script.
    """
    parser = argparse.ArgumentParser(
        description='Disable root access for an Amazon SageMaker notebook instance.'
        )
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('-r', '--region', required=True, type=str,
                        help='AWS region where the SageMaker notebook instance is located')
    parser.add_argument('-i', '--instance', required=True, type=str,
                        help='SageMaker notebook instance name')
    return parser.parse_args()

def disable_root_access(sagemaker, instance_name):
    """
    Disable root access for the given SageMaker notebook instance.
    """
    try:
        sagemaker.update_notebook_instance(
            NotebookInstanceName=instance_name,
            RootAccess='Disabled'
        )
        print(f"Success! Root access is disabled for the notebook instance '{instance_name}'.")
    except ClientError as error:
        print(f"An error occurred: {error.response['Error']['Message']}")

def main():
    """
    Main function of the script.
    """
    args = parse_args()
    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    sagemaker = session.client('sagemaker')

    disable_root_access(sagemaker, args.instance)

if __name__ == "__main__":
    main()
