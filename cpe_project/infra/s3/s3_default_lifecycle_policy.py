"""
A script to enable versioning and set a lifecycle policy for an AWS S3 bucket.

This script allows the user to enable versioning and set a lifecycle policy
for a single specified S3 bucket or all buckets in an AWS account.
The lifecycle policy includes transitioning to different storage classes
after specified durations and cleaning up incomplete multipart uploads.

The user must provide their AWS profile name for the script to establish an AWS session.
They can specify a single bucket by its name or choose to modify all buckets in the account.

Command line arguments:
    -p, --profile: (required) AWS profile name for SSO login
    -b, --bucket: Name of a single bucket
    -a, --all: If set, the script will modify all buckets in the account

Example usage:
    python3 script_name.py --profile my_profile --bucket my_bucket
    python3 script_name.py --profile my_profile --all

Modules used:
    - argparse: For parsing command line arguments
    - boto3: For interacting with AWS services
    - botocore.exceptions: For handling exceptions that Boto3 might raise
"""

import argparse
import boto3
from botocore.exceptions import ClientError

def enable_bucket_versioning(s3_client, bucket_name):
    """
    Enables versioning for the specified S3 bucket if it's not already enabled.

    Parameters:
        s3_client (botocore.client.S3): The S3 client.
        bucket_name (str): The name of the bucket.

    Raises:
        botocore.exceptions.ClientError: If an error occurs while trying to enable versioning.
    """
    try:
        versioning_status = s3_client.get_bucket_versioning(Bucket=bucket_name)
        if versioning_status.get('Status') != 'Enabled':
            s3_client.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={
                    'Status': 'Enabled'
                }
            )
            print(f"Enabled versioning for bucket {bucket_name}.")
    except ClientError as error:
        print(f"An error occurred while enabling bucket versioning: "
              f"{error.response['Error']['Message']}")


def set_bucket_lifecycle_policy(s3_client, bucket_name, lifecycle_policy):
    """
    Sets a lifecycle policy for the specified S3 bucket.

    Parameters:
        s3_client (botocore.client.S3): The S3 client.
        bucket_name (str): The name of the bucket.
        lifecycle_policy (dict): The lifecycle policy to be set.

    Raises:
        botocore.exceptions.ClientError: If an error occurs
        while trying to set the lifecycle policy.
    """
    try:
        s3_client.put_bucket_lifecycle_configuration(
            Bucket=bucket_name,
            LifecycleConfiguration=lifecycle_policy
        )
        print(f"Successfully set lifecycle policy for bucket {bucket_name}.")
    except ClientError as error:
        print(f"An error occurred while setting lifecycle policy: "
              f"{error.response['Error']['Message']}")

def main():
    """
    Parses command-line arguments, establishes an AWS session,
    and enables S3 bucket versioning and sets lifecycle policy.
    """
    parser = argparse.ArgumentParser(description="Modify S3 Bucket Properties")
    parser.add_argument('-p','--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('-b','--bucket', type=str,
                        help='Name of a single bucket')
    parser.add_argument('-a','--all', action='store_true',
                        help='Modify all buckets in the account')
    parser.add_argument('-r', '--region', required=True,
                        help='AWS region for the S3 client')


    args = parser.parse_args()

    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    s3_client = session.client('s3')

    lifecycle_policy = {
        'Rules': [
            {
                'ID': 'myorg-securityhub-s3.13-default-lifecycle-policy',
                'Status': 'Enabled',
                'Filter': {
                    'Prefix': ''
                },
                'Transitions': [
                    {
                        'Days': 0,
                        'StorageClass': 'INTELLIGENT_TIERING'
                    }
                ],
                'NoncurrentVersionTransitions': [
                    {
                        'NoncurrentDays': 30,
                        'StorageClass': 'GLACIER_IR'
                    }
                ],
                'Expiration': {
                    'ExpiredObjectDeleteMarker': True
                },
                'NoncurrentVersionExpiration': {
                    'NoncurrentDays': 180,
                    'NewerNoncurrentVersions':1
                },
                'AbortIncompleteMultipartUpload': {
                    'DaysAfterInitiation': 7
                }
            }
        ]
    }


    if args.all:
        response = s3_client.list_buckets()
        for bucket in response['Buckets']:
            bucket_name = bucket['Name']
            enable_bucket_versioning(s3_client, bucket_name)
            set_bucket_lifecycle_policy(s3_client, bucket_name, lifecycle_policy)
    elif args.bucket:
        enable_bucket_versioning(s3_client, args.bucket)
        set_bucket_lifecycle_policy(s3_client, args.bucket, lifecycle_policy)
    else:
        print("No buckets specified.")

if __name__ == "__main__":
    main()
