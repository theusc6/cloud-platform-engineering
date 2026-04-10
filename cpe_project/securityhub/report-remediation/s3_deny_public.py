"""
Deny public access to S3 buckets
"""

import argparse
import boto3

# Ensure a profile argument is passed in
parser = argparse.ArgumentParser()
parser.add_argument('-p', '--profile', required=True, help='AWS profile name for SSO login')
args = parser.parse_args()

# Set up boto3 client
session = boto3.Session(profile_name=args.profile)
s3_client = session.client('s3')

# List all S3 buckets
buckets = s3_client.list_buckets()['Buckets']

# Check permissions and remediate if needed
for bucket in buckets:
    bucket_name = bucket['Name']
    print(f"Checking permissions for {bucket_name}")
    response = s3_client.get_public_access_block(Bucket=bucket_name)
    public_access_block_config = response['PublicAccessBlockConfiguration']

    # Check if public access is already blocked
    if all(public_access_block_config.values()):
        print(f"Permissions for {bucket_name} are properly configured")
    else:
        print(f"Bucket permissions are NOT properly configured for {bucket_name}")
        print(f"Fixing permissions for bucket: {bucket_name}")
        s3_client.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
        print(f"Rechecking {bucket_name}")
        response = s3_client.get_public_access_block(Bucket=bucket_name)
        public_access_block_config = response['PublicAccessBlockConfiguration']
        if all(public_access_block_config.values()):
            print(f"Permissions for {bucket_name} are now properly configured")
        else:
            print(f"The script was unable to resolve permissions for {bucket_name}. Please check in the UI.")
