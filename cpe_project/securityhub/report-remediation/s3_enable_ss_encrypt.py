"""
enable Server Side encryption for all S3 buckets in an AWS account
"""

import argparse
import boto3
from botocore.exceptions import ClientError

# Ensure a profile argument is passed in
parser = argparse.ArgumentParser(description='List and remediate S3 buckets without server-side encryption.')
parser.add_argument('-p', '--profile', help='AWS profile to use')
args = parser.parse_args()

# Create the S3 client
session = boto3.Session(profile_name=args.profile)
s3 = session.client('s3')

# List all S3 bucket's current server side encryption settings
for bucket in s3.list_buckets()['Buckets']:
    bucket_name = bucket['Name']
    print(f"Bucket: {bucket_name}")

    try:
        encryption = s3.get_bucket_encryption(Bucket=bucket_name)
        print(encryption)
    except ClientError as error:
        # If the bucket does not have encryption enabled, remediate it
        if error.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
            print(f"No encryption found, adding default encryption to {bucket_name}")
            s3.put_bucket_encryption(
                Bucket=bucket_name,
                ServerSideEncryptionConfiguration={
                    'Rules': [{
                        'ApplyServerSideEncryptionByDefault': {'SSEAlgorithm': 'AES256'}
                    }]
                }
            )
            print(f"Encryption enabled for bucket {bucket_name}")

            # Verify that encryption has been enabled
            try:
                encryption = s3.get_bucket_encryption(Bucket=bucket_name)
                print(f"Encryption verified for bucket {bucket_name}")
                print(encryption)
            except ClientError as e:
                print(f"The script was unable to resolve encryption for {bucket_name}. Please check in the AWS console.")
        else:
            print(f"Unexpected error occurred: {error}")
