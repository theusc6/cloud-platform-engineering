#!/usr/bin/env python3

"""
Get an S3 bucket size.

"""

import argparse
import boto3
from botocore.exceptions import ClientError

# Ensure a profile argument is passed in
parser = argparse.ArgumentParser(description='Get an S3 bucket size.')
parser.add_argument('-p', '--profile', required=True, type=str,
                    help='AWS profile name for SSO login')
parser.add_argument('-b', '--bucket-name', required=True, type=str,
                    help='Name of the bucket to get the size of')
args = parser.parse_args()

# Set up boto3 client
session = boto3.Session(profile_name=args.profile)
s3_client = session.client('s3')

def get_s3_bucket_size(name_of_bucket):
    """
    Get total size of S3 bucket.
    """
    total_size = 0
    continuation_token = ''

    try:
        # Iterate through the objects and calculate the total size
        while True:
            if continuation_token:
                response = s3_client.list_objects_v2(Bucket=name_of_bucket,
                                                          ContinuationToken=continuation_token)
            else:
                response = s3_client.list_objects_v2(Bucket=name_of_bucket)

            if 'Contents' in response:
                for obj in response['Contents']:
                    total_size += obj['Size']

            if not response.get('IsTruncated'):
                break

            continuation_token = response['NextContinuationToken'] or ''

        # Convert total_size to human-readable format
        size, unit = format_size(total_size)

        print(f"The size of the bucket '{name_of_bucket}' is approximately: {size:.2f} {unit}")
    except ClientError as error:
        print(f"An error occurred: {error.response['Error']['Message']}")

def format_size(size_in_bytes):
    """
    Convert size in bytes to human-readable format.
    """
    units = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    while size_in_bytes >= 1024 and unit_index < len(units) - 1:
        size_in_bytes /= 1024
        unit_index += 1
    return size_in_bytes, units[unit_index]

# Usage
bucket_name = args.bucket_name
get_s3_bucket_size(bucket_name)
