"""
This script automates the process of enabling versioning for AWS S3 buckets using
the AWS SDK for Python (Boto3).
"""

#!/usr/bin/env python3

import argparse
import boto3

def get_bucket_names(s_three):
    """
    Returns a list of all bucket names.
    """
    response = s_three.list_buckets()
    return [bucket['Name'] for bucket in response['Buckets']]

def is_versioning_enabled(bucket):
    """
    Returns True if versioning is enabled for the given bucket, False otherwise.
    """
    versioning = bucket.Versioning()
    return versioning.status == 'Enabled'

def enable_versioning(bucket):
    """
    Enables versioning for the given bucket.
    """
    versioning = bucket.Versioning()
    versioning.enable()

def main():
    """
    Main function.
    """
    # Ensure a profile argument is passed in
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--profile', required=True, help='AWS profile name for SSO login')
    args = parser.parse_args()

    # Set up SSO login
    session = boto3.Session(profile_name=args.profile)
    s_three = session.resource('s3')

    # List all buckets and enable versioning for those that don't already have it
    for bucket in s_three.buckets.all():
        try:
            if not is_versioning_enabled(bucket):
                enable_versioning(bucket)
                print(f"Enabled versioning for bucket {bucket.name}")
            else:
                print(f"Versioning is already enabled for bucket {bucket.name}")
        except Exception as error:
            print(f"Error: {error} occurred while processing bucket {bucket.name}")

if __name__ == '__main__':
    main()
