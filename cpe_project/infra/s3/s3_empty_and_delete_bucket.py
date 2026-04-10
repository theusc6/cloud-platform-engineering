#!/usr/bin/env python3

""""
Empty and delete an S3 bucket.

"""

import argparse
import boto3
from botocore.exceptions import ClientError

# Ensure a profile argument is passed in
parser = argparse.ArgumentParser(description='Empty and delete an S3 bucket.')
parser.add_argument('-p', '--profile', required=True, type=str,
                    help='AWS profile name for SSO login')
parser.add_argument('-b', '--bucket-name', required=True, type=str,
                    help='Name of the bucket to empty and delete')
args = parser.parse_args()

# Set up boto3 client
session = boto3.Session(profile_name=args.profile)
s3_client = session.client('s3')

def empty_s3_bucket(name_of_bucket):
    """
    Empty the bucket by deleting all objects in the bucket.
    """
    try:
        # Delete all objects in the bucket
        response = s3_client.list_objects_v2(Bucket=name_of_bucket)
        objects = response.get('Contents', [])

        if len(objects) > 0:
            objects_to_delete = [{'Key': obj['Key']} for obj in objects]
            s3_client.delete_objects(Bucket=name_of_bucket, Delete={'Objects': objects_to_delete})
            print(f"Successfully emptied the bucket '{name_of_bucket}'.")
        else:
            print(f"The bucket '{name_of_bucket}' is already empty.")

    except ClientError as error:
        print(f"An error occurred while emptying the bucket '{name_of_bucket}': "
              f"{error.response['Error']['Message']}"
        )
        return

def delete_s3_bucket(name_of_bucket):
    """
    Delete the bucket.
    """
    try:
        # Delete the bucket
        s3_client.delete_bucket(Bucket=name_of_bucket)
        print(f"Successfully deleted the bucket '{name_of_bucket}'.")
    except ClientError as error:
        print(f"An error occurred while deleting the bucket '{name_of_bucket}': "
              f"{error.response['Error']['Message']}"
        )

# Usage
bucket_name = args.bucket_name

empty_s3_bucket(bucket_name)

# Prompt the user to continue
while True:
    confirm = input("Do you want to delete the bucket? (Y/n): ")
    if confirm.lower() in ['y', 'yes', '']:
        delete_s3_bucket(bucket_name)
        break
    if confirm.lower() in ['n', 'no']:
        print("Operation canceled.")
        break

    print("Invalid input. Please enter Y, N, or leave it blank.")
