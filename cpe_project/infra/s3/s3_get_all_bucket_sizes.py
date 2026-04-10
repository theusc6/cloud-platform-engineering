#!/usr/bin/env python3

"""
Get all S3 bucket sizes from the provided account.

"""

import argparse
import boto3
from botocore.exceptions import ClientError

# Ensure a profile argument is passed in
parser = argparse.ArgumentParser(description='List all S3 buckets and their sizes.')
parser.add_argument('-p', '--profile', required=True, type=str,
                    help='AWS profile name for SSO login')
parser.add_argument('-s', '--size', type=int, default=0,
                    help='Minimum size in MB for objects to be included in output')
parser.add_argument('-b', '--bucket-size-only', action='store_true',
                    help='Only show the size of each bucket and not its contents')
args = parser.parse_args()

# Set up boto3 client
session = boto3.Session(profile_name=args.profile)
s3_client = session.client('s3')

# Convert size to bytes
min_size = args.size * 1024 * 1024

# Define function to convert size to human-readable format
def convert_size(size):
    """
    convert size in bytes to human-readable format
    """
    if size < 1024:
        return f"{size} B"
    size /= 1024
    if size < 1024:
        return f"{size:.2f} MB"
    size /= 1024
    if size < 1024:
        return f"{size:.2f} GB"
    size /= 1024
    return f"{size:.2f} TB"

# Get all S3 buckets
buckets = s3_client.list_buckets()['Buckets']

# Iterate through each bucket and print its name and size
for bucket in buckets:
    try:
        # pylint: disable=invalid-name
        total_size = 0
        objects = []
        if args.bucket_size_only:
            response = s3_client.list_objects_v2(Bucket=bucket['Name'], MaxKeys=0)
            if 'Stats' in response:
                total_size = response['Stats']['TotalSize']
        else:
            response = s3_client.list_objects_v2(Bucket=bucket['Name'])
            if 'Contents' in response:
                for obj in response['Contents']:
                    obj_size = obj['Size']
                    if obj_size != 0 and obj_size >= min_size:
                        total_size += obj_size
                        objects.append((obj['Key'], obj_size))

                # Sort objects by size
                objects.sort(key=lambda x: x[1], reverse=True)

        size_str = convert_size(total_size)
        print(f"{bucket['Name']}: {size_str}")
        for obj in objects:
            obj_size_str = convert_size(obj[1])
            print(f"  {obj[0]}: {obj_size_str}")
    except ClientError as error:
        if error.response['Error']['Code'] == 'AccessDenied':
            print(f"No permission to access bucket {bucket['Name']}")
        elif error.response['Error']['Code'] == 'NoSuchBucket':
            print(f"Bucket {bucket['Name']} does not exist")
        else:
            print(f"Failed to get size of bucket {bucket['Name']}: {error}")
