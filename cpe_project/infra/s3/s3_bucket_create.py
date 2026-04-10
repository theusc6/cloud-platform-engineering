#!/usr/bin/env python3

"""
This module creates a compliant bucket against 
AWS Foundational Security Best Practices v1.0.0.

https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html
Coverages for:
[S3.1] S3 Block Public Access setting should be enabled
[S3.4] S3 buckets should have server-side encryption enabled
[S3.8] S3 Block Public Access setting should be enabled at the bucket-level
[S3.9] S3 bucket server access logging should be enabled
[S3.14] S3 buckets should use versioning


"""

import sys
import argparse
import boto3
from botocore.exceptions import ClientError

# Ensure a profile argument is passed in
parser = argparse.ArgumentParser(description='Create a compliant AWS S3 bucket.')
parser.add_argument('-b', '--bucket', required=True, type=str, help='AWS bucket name to create')
parser.add_argument('-f', '--folder', required=False, type=str, dest='folder_name',
                    help='AWS folder name to create in the new bucket')
parser.add_argument('-p', '--profile', required=True, type=str,
                    help='AWS profile name for SSO login')
args = parser.parse_args()

# args
bucket_name = args.bucket

# Set up boto3 client
session = boto3.Session(profile_name=args.profile)
s3_client = session.client('s3')

# Create a bucket
try:
    s3_client.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={
            'LocationConstraint': 'us-west-2'
        })
except ClientError as e:
    if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
        print('Bucket already exists.')
        sys.exit()
    else:
        raise

# Create a folder if a folder name is provided
if args.folder_name:
    folder_name = args.folder_name
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=f'{folder_name}/'
        )
    except ClientError as e:
        print(f"Failed to create folder: {e}")
else:
    print("No folder argument provided. Folder not created.")

# Set the expiration policy for the contents of the folder
try:
    s3_client.put_bucket_lifecycle_configuration(
        Bucket=bucket_name,
        LifecycleConfiguration={
            'Rules': [
                {
                    'ID': 'Expire objects in the reports folder after 365 days',
                    'Status': 'Enabled',
                    'Prefix': 'folder_name/',
                    'NoncurrentVersionExpiration': {
                        'NoncurrentDays': 365
                    }
                }
            ]
        }
    )
except ClientError as e:
    print(f"Failed to set bucket lifecycle configuration: {e}")

# Enable server-side encryption
try:
    s3_client.put_bucket_encryption(
        Bucket=bucket_name,
        ServerSideEncryptionConfiguration={
            'Rules': [
                {
                    'ApplyServerSideEncryptionByDefault': {
                        'SSEAlgorithm': 'AES256'
                    }
                }
            ]
        }
    )
except ClientError as e:
    print(f"Failed to enable server-side encryption: {e}")

# Enable bucket versioning
try:
    s3_client.put_bucket_versioning(
        Bucket=bucket_name,
        VersioningConfiguration={
            'Status': 'Enabled'
        }
    )
except ClientError as e:
    print(f"Failed to enable bucket versioning: {e}")

# Block all public access
try:
    s3_client.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        }
    )
except ClientError as e:
    print(f"Failed to block public access: {e}")

# Enable bucket logging
try:
    s3_client.put_bucket_logging(
        Bucket=bucket_name,
        BucketLoggingStatus={
            'LoggingEnabled': {
                'TargetBucket': bucket_name,
                'TargetPrefix': 'logs/'
            }
        }
    )
except ClientError as e:
    print(f"Failed to enable bucket logging: {e}")

# Set tags
try:
    s3_client.put_bucket_tagging(
        Bucket=bucket_name,
        Tagging={
            'TagSet': [
                {
                    'Key': 'Category',
                    'Value': 'DevSecOps'
                },
                {
                    'Key': 'Product',
                    'Value': 'S3 Bucket'
                }
            ]
        }
    )
except ClientError as e:
    print(f"Failed to set tags: {e}")
