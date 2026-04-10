"""
This script is used to improve the security of Amazon S3 buckets in AWS.
It offers functionalities to enable logging, 
set bucket policies, enable versioning, and set lifecycle policies. 
It also creates a logging bucket with a specific tag.

The script works with AWS SSO profiles and can be used on
either a single bucket or all buckets in an account.

Usage:

    python script_name.py --profile <AWS SSO profile> 
    --bucket <bucket name> # To perform operations on a single bucket.
    
    python script_name.py --profile <AWS SSO profile> --all                  
    # To perform operations on all buckets in the account.
"""

import argparse
import json
import boto3

from botocore.exceptions import ClientError

def create_logging_bucket(s3_client, bucket_name):
    """
    Creates an S3 bucket to store access logs and add a tag.
    """
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} already exists.")
    except ClientError:
        print(f"Bucket {bucket_name} does not exist. Creating...")
        try:
            if s3_client.meta.region_name == 'us-east-1':
                s3_client.create_bucket(Bucket=bucket_name)
            else:
                s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={
                        'LocationConstraint': s3_client.meta.region_name
                    }
                )
            print(f"Bucket {bucket_name} created.")
        except ClientError as error:
            print(f"An error occurred while creating bucket: {error.response['Error']['Message']}")
            return  # Exit function early if bucket creation fails

    # Moved tagging block here to tag both new and existing buckets.
    try:
        s3_client.put_bucket_tagging(
            Bucket=bucket_name,
            Tagging={
                'TagSet': [
                    {
                        'Key': 'Category',
                        'Value': 'Security'
                    },
                ]
            }
        )
        print(f"Bucket {bucket_name} tagged with 'Category: Security'.")
    except ClientError as error:
        print(f"Unable to apply tag to bucket {bucket_name}. "
              f"Error: {error.response['Error']['Message']}")

def enable_logging_for_bucket(s3_client, bucket_name, logging_bucket_name):
    """
    Enables S3 access logging for a specified bucket.
    """
    if 'myorg-securityhub-s3.9accesslogging' not in bucket_name:
        try:
            s3_client.put_bucket_logging(
                Bucket=bucket_name,
                BucketLoggingStatus={
                    'LoggingEnabled': {
                        'TargetBucket': logging_bucket_name,
                        'TargetPrefix': f"{bucket_name}/"
                    }
                }
            )
            print(f"Enabled logging for bucket {bucket_name}.")
        except ClientError as error:
            print(f"An error occurred: {error.response['Error']['Message']}")

def set_bucket_policy(s3_client, bucket_name, account_id):
    """
    Sets a bucket policy to deny HTTP.
    """
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError as error:
        print(f"An error occurred while checking if bucket exists: "
              f"{error.response['Error']['Message']}")
        return  # Exit function early if bucket head check fails

    bucket_policy = {
        'Version': '2012-10-17',
        'Statement': [{
            'Sid': 'RequireSSLOnly',
            'Effect': 'Deny',
            'Principal': '*',
            'Action': 's3:*',
            'Resource': [
                f'arn:aws:s3:::{bucket_name}/*',
                f'arn:aws:s3:::{bucket_name}'
            ],
            'Condition': {
               'Bool': {
                  'aws:SecureTransport': 'false'
               }
            }
        },
        {
            "Sid": "S3ServerAccessLogsPolicy",
            "Effect": "Allow",
            "Principal": {
                "Service": "logging.s3.amazonaws.com"
            },
            "Action": [
                "s3:PutObject"
            ],
            "Resource": f"arn:aws:s3:::{bucket_name}/*",
            "Condition": {
                "ArnLike": {
                    "aws:SourceArn": "arn:aws:s3:::*"
                },
                "StringEquals": {
                    "aws:SourceAccount": f"{account_id}"
                }
            }
        }
    ]
}
    policy_string = json.dumps(bucket_policy)
    try:
        s3_client.put_bucket_policy(Bucket=bucket_name, Policy=policy_string)
        print(f"Set bucket policy to deny HTTP for bucket {bucket_name}.")
    except ClientError as error:
        print(f"An error occurred while setting bucket policy: "
              f"{error.response['Error']['Message']}")

def enable_bucket_versioning(s3_client, bucket_name):
    """
    Enables bucket versioning.
    """
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError as error:
        print(f"An error occurred while checking if bucket exists: "
              f"{error.response['Error']['Message']}")
        return  # Exit function early if bucket head check fails

    try:
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

def set_bucket_lifecycle_policy(s3_client, bucket_name):
    """
    Sets a bucket lifecycle policy.
    """
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError as error:
        print(f"An error occurred while checking if bucket exists: "
              f"{error.response['Error']['Message']}")
        return  # Exit function early if bucket head check fails

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
                    'DaysAfterInitiation': 30
                }
            }
        ]
    }

    s3_client.put_bucket_lifecycle_configuration(
        Bucket=bucket_name,
        LifecycleConfiguration=lifecycle_policy
    )
    print(f"Set lifecycle policy for bucket {bucket_name}.")


def main():
    """
    Parses command-line arguments, establishes an AWS session, and enables S3 access logging.
    """
    parser = argparse.ArgumentParser(description="Enable S3 access logging")
    parser.add_argument('-p','--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('-b','--bucket', type=str,
                        help='Name of a single bucket')
    parser.add_argument('-a','--all', action='store_true',
                        help='Enable logging for all buckets in the account')
    parser.add_argument('-r', '--region', required=True,
                    help='AWS region for the S3 client')
    args = parser.parse_args()

    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    s3_client = session.client('s3')
    account_id = session.client('sts').get_caller_identity().get('Account')

    if args.all:
        response = s3_client.list_buckets()
        for bucket in response['Buckets']:
            bucket_name = bucket['Name']
            bucket_info = s3_client.get_bucket_location(Bucket=bucket_name)
            bucket_region = bucket_info['LocationConstraint']
            if bucket_region is None:
                bucket_region = 'us-east-1'
            bucket_region_s3_client = session.client('s3', region_name=bucket_region)
            logging_bucket_name = f"myorg-securityhub-s3.9accesslogging-{account_id}-{bucket_region}"
            create_logging_bucket(bucket_region_s3_client, logging_bucket_name)
            set_bucket_policy(bucket_region_s3_client, logging_bucket_name, account_id)
            enable_bucket_versioning(bucket_region_s3_client, logging_bucket_name)
            set_bucket_lifecycle_policy(bucket_region_s3_client, logging_bucket_name)
            enable_logging_for_bucket(bucket_region_s3_client, bucket['Name'], logging_bucket_name)
    elif args.bucket:
        bucket_region = s3_client.get_bucket_location(Bucket=args.bucket)['LocationConstraint']
        if bucket_region is None:
            bucket_region = 'us-east-1'
        bucket_region_s3_client = session.client('s3', region_name=bucket_region)
        logging_bucket_name = f"myorg-securityhub-s3.9accesslogging-{account_id}-{bucket_region}"
        create_logging_bucket(bucket_region_s3_client, logging_bucket_name)
        set_bucket_policy(bucket_region_s3_client, logging_bucket_name, account_id)
        enable_bucket_versioning(bucket_region_s3_client, logging_bucket_name)
        set_bucket_lifecycle_policy(bucket_region_s3_client, logging_bucket_name)
        enable_logging_for_bucket(bucket_region_s3_client, args.bucket, logging_bucket_name)
    else:
        print("No buckets specified.")

if __name__ == "__main__":
    main()
