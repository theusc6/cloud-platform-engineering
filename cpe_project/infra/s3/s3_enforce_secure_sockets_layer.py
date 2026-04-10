"""
Update S3 bucket policies to require SSL in 
accordance with SecurityHub S3.5
"""
import argparse
import json
import boto3
from botocore.exceptions import ClientError

# Ensure a profile argument is passed in
parser = argparse.ArgumentParser(description='Update S3 bucket policies to require SSL.')
parser.add_argument('-p', '--profile', required=True, type=str,
                    help='AWS profile name for SSO login')
parser.add_argument('-a', '--all-buckets', action='store_true',
                    help='Update policies for all buckets in the account')
parser.add_argument('-b', '--bucket-name', type=str,
                    help='Name of the specific bucket to update the policy of')
parser.add_argument('-r', '--region', required=True,
                    help='AWS region for the S3 client')

args = parser.parse_args()

# Set up boto3 client
session = boto3.Session(profile_name=args.profile, region_name=args.region)
s3_client = session.client('s3')

def policy_exists(existing_policy, new_policy):
    """
    Check if the new_policy exists in the existing_policy.
    """
    for statement in existing_policy['Statement']:
        if statement == new_policy['Statement'][0]:
            return True
    return False


def update_bucket_policy(name_of_bucket):
    """
    Update S3 bucket policy to require SSL.
    """
    bucket_policy = {
    'Version': '2012-10-17',
    'Statement': [
        {
            'Sid': 'RequireSSLOnly',
            'Effect': 'Deny',
            'Principal': '*',
            'Action': 's3:*',
            'Resource': [
                f'arn:aws:s3:::{name_of_bucket}/*',
                f'arn:aws:s3:::{name_of_bucket}'
            ],
            'Condition': {
                'Bool': {
                    'aws:SecureTransport': 'false'
                }
            }
        }
    ]
}

    try:
        # Get the existing bucket policy
        response = s3_client.get_bucket_policy(Bucket=name_of_bucket)
        existing_policy = json.loads(response['Policy'])

        # Check if the SSL policy already exists
        if policy_exists(existing_policy, bucket_policy):
            print(f"The bucket policy for '{name_of_bucket}' already requires SSL.")
        else:
            # Append the new policy statement to the existing policy
            existing_policy['Statement'].extend(bucket_policy['Statement'])

            # Convert the policy to a JSON string
            updated_policy_json = json.dumps(existing_policy)

            # Set the updated bucket policy
            s3_client.put_bucket_policy(Bucket=name_of_bucket, Policy=updated_policy_json)

            print(f"The bucket policy for '{name_of_bucket}' has been updated to require SSL.")
    except ClientError as error:
        if error.response['Error']['Code'] == 'NoSuchBucketPolicy':
            # If no policy exists, create a new policy
            s3_client.put_bucket_policy(Bucket=name_of_bucket, Policy=json.dumps(bucket_policy))
            print(f"A new bucket policy for '{name_of_bucket}' has been created to require SSL.")
        else:
            print(f"An error occurred: {error.response['Error']['Message']}")

def get_all_bucket_names():
    """
    Retrieve a list of all bucket names in the account.
    """
    response = s3_client.list_buckets()
    all_buckets = response['Buckets']
    bucket_names = [bucket['Name'] for bucket in all_buckets]
    return bucket_names

# Usage
if args.all_buckets:
    buckets = get_all_bucket_names()
    for bucket in buckets:
        print(f"Updating policy for bucket: {bucket}")
        update_bucket_policy(bucket)
else:
    if args.bucket_name:
        bucket_name = args.bucket_name
        update_bucket_policy(bucket_name)
    else:
        print("Please provide either the --all-buckets option or the --bucket-name option.")
