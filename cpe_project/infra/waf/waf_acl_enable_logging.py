"""
Script to Configure Access Logging for AWS WAFv2 ACLs.

This script enables the logging of AWS WAFv2 ACLs to an Amazon S3 bucket.
The user has the option to specify a profile for SSO login and a specific region.
Logs from the WAFv2 ACLs will be stored in the specified or created S3 bucket.

Usage:
    python script_name.py --profile your_profile_name --region us-west-2
"""

import argparse
import json
import boto3

from botocore.exceptions import ClientError


def parse_args():
    """
    Parse command-line arguments passed to the script.
    """
    parser = argparse.ArgumentParser(
        description='Configure Access Logging for AWS WAF Acl(s).'
        )
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('-r', '--region', default='us-west-2', type=str,
                        help='AWS region (default: us-west-2)')
    parser.add_argument('-wa', '--waf_acl', required=False, type=str,
                        help='Id of a single WAF acl for access logging')
    parser.add_argument('-a', '--all', required=False, action='store_true',
                        help='Enable access logging for all load balancers')
    return parser.parse_args()

def create_s3_bucket(session, bucket_name, account_id, region):
    """
    This function creates an Amazon S3 bucket with a specified name, policy, tagging,
    versioning configuration, public access block configuration, and lifecycle policy.

    Parameters:
    session (boto3.Session): An AWS session object created by Boto3.
    bucket_details (dict): The details of the S3 bucket to be created.

    Returns:
    None
    """
    s3_client = session.client('s3')

    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
                {
            "Sid": "AWSLogDeliveryWrite",
            "Effect": "Allow",
            "Principal": {
                "Service": "delivery.logs.amazonaws.com"
            },
            "Action": "s3:PutObject",
            "Resource": f"arn:aws:s3:::{bucket_name}/*/AWSLogs/{account_id}/*",
            "Condition": {
                "StringEquals": {
                "s3:x-amz-acl": "bucket-owner-full-control",
                "aws:SourceAccount": [f"{account_id}"]
                },
                "ArnLike": {
                "aws:SourceArn": [f"arn:aws:logs:{region}:{account_id}:*"]
                }
            }
            },
            {
            "Sid": "AWSLogDeliveryAclCheck",
            "Effect": "Allow",
            "Principal": {
                "Service": "delivery.logs.amazonaws.com"
            },
            "Action": "s3:GetBucketAcl",
            "Resource": f"arn:aws:s3:::{bucket_name}",
            "Condition": {
                "StringEquals": {
                "aws:SourceAccount": [f"{account_id}"]
                },
                "ArnLike": {
                "aws:SourceArn": [f"arn:aws:logs:{region}:{account_id}:*"]
                }
            }
            },
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": f"arn:aws:iam::{account_id}:root"
                },
                "Action": "s3:PutObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*"
            },
            {
                "Sid": "RequireSSLOnly",
                "Effect": "Deny",
                "Principal": "*",
                "Action": "s3:*",
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}/*",
                    f"arn:aws:s3:::{bucket_name}"
                ],
                "Condition": {
                    "Bool": {
                        "aws:SecureTransport": "false"
                    }
                }
            }
        ]
    }

    try:
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': region}
        )
        print(f"Bucket {bucket_name} has now been created.")
    except ClientError as client_error:
        if client_error.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print(f"Bucket {bucket_name} already exists.")
        else:
            print(f"An error occurred while creating the bucket: "
                  f"{client_error.response['Error']['Message']}")
            return False

    try:
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )
        print(f"SSL is now required for bucket {bucket_name}.")
    except ClientError as client_error:
        print(f"An error occurred while applying the bucket policy: "
              f"{client_error.response['Error']['Message']}")

    try:
        s3_client.put_bucket_tagging(
            Bucket=bucket_name,
            Tagging={'TagSet': [{'Key': 'Category', 'Value': 'Security'}]}
        )
        print(f"Tags have been applied to bucket {bucket_name}.")
    except ClientError as client_error:
        print(f"An error occurred while applying bucket tags: "
              f"{client_error.response['Error']['Message']}")

    try:
        s3_client.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={
                    'Status': 'Enabled'
                }
            )
        print(f"Versioning is enabled for for {bucket_name}.")
    except ClientError as client_error:
        print(f"An error occurred while enabling bucket versioning: "
              f"{client_error.response['Error']['Message']}")

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
        print(f"Public access is blocked for {bucket_name}.")
    except ClientError as client_error:
        print(f"An error occurred while blocking public access: "
              f"{client_error.response['Error']['Message']}")

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

    log_bucket_name= f"myorg-securityhub-s3.9accesslogging-{account_id}-{region}"

    try:
        s3_client.put_bucket_lifecycle_configuration(
            Bucket=bucket_name,
            LifecycleConfiguration=lifecycle_policy
        )
        print(f"Applied bucket lifecycle policy for bucket {bucket_name}.")
    except ClientError as client_error:
        print(f"An error occurred while applying lifecycle policy: "
              f"{client_error.response['Error']['Message']}")

    if 'myorg-securityhub-s3.9accesslogging' not in bucket_name:
        try:
            s3_client.put_bucket_logging(
                Bucket=bucket_name,
                BucketLoggingStatus={
                    'LoggingEnabled': {
                        'TargetBucket': log_bucket_name,
                        'TargetPrefix': f"{bucket_name}/"
                    }
                }
            )
            print(f"Enabled logging for bucket {bucket_name}. "
                  f"Logging to {log_bucket_name}.")
        except ClientError as error:
            print(f"An error occurred: {error.response['Error']['Message']}")
    return True

def process_waf_acls(session, account_id, region, waf_acl_id=None, all_acls=False):
    """
    Loop through WAFv2 Web ACLs and enable logging.
    If waf_acl_id is provided, it logs only for that specific ACL.
    If all_acls is True, it logs for all ACLs.
    """
    wafv2_client = session.client('wafv2')

    if waf_acl_id:
        try:
            # First, get the name of the WebACL with the given Id
            response = wafv2_client.list_web_acls(Scope='REGIONAL')
            web_acl_name = None
            for web_acl in response['WebACLs']:
                if web_acl['Id'] == waf_acl_id:
                    web_acl_name = web_acl['Name']
                    break

            if not web_acl_name:
                print(f"No WebACL found with Id: {waf_acl_id}")
                return

            response = wafv2_client.get_web_acl(Name=web_acl_name, Id=waf_acl_id, Scope='REGIONAL')
            web_acl = response['WebACL']
            web_acl_arn = web_acl['ARN']

            # Construct a unique bucket name for this ACL
            bucket_name = f"aws-waf-logs-myorg-sechub-waf11-{account_id}-{region}"
            if create_s3_bucket(session, bucket_name, account_id, region):
                enable_waf_logging(session, web_acl_arn, bucket_name, waf_acl_id)

        except ClientError as client_error:
            print(f"An error occurred: {client_error}")

    elif all_acls:
        try:
            response = wafv2_client.list_web_acls(Scope='REGIONAL')
            for web_acl in response['WebACLs']:
                web_acl_name = web_acl['Name']
                web_acl_id = web_acl['Id']

                response_detail = wafv2_client.get_web_acl(Name=web_acl_name,
                                                           Id=web_acl_id, Scope='REGIONAL')
                web_acl_detail = response_detail['WebACL']
                web_acl_arn = web_acl_detail['ARN']

                # Construct a unique bucket name for each ACL
                bucket_name = f"aws-waf-logs-myorg-sechub-waf11-{account_id}-{region}"

                if create_s3_bucket(session, bucket_name, account_id, region):
                    enable_waf_logging(session, web_acl_arn, bucket_name, waf_acl_id)

        except ClientError as client_error:
            print(f"An error occurred: {client_error}")

def enable_waf_logging(session, acl_arn, bucket_name, waf_acl_id):
    """
    Enable logging for the given WAFv2 Web ACL.
    """
    wafv2_client = session.client('wafv2')
    try:
        wafv2_client.put_logging_configuration(
            LoggingConfiguration={
                'ResourceArn': acl_arn,
                'LogDestinationConfigs': [
                    f"arn:aws:s3:::{bucket_name}/{waf_acl_id}",
                ],
                'RedactedFields': [
                    # Here you can specify which fields to redact from the logs.
                    # As an example, let's redact the URI path:
                    {
                        'SingleHeader': {
                            'Name': 'UriPath'
                        }
                    },
                ]
            }
        )
        print(f"Logging enabled for WAF ACL with ARN: {acl_arn}. "
              f"Logs are directed to bucket: {bucket_name}/{waf_acl_id}")
    except ClientError as client_error:
        print(f"An error occurred while setting up logging for {acl_arn}. Error: {client_error}")

def main():
    """
    Main function of the script.
    """
    args = parse_args()
    session = boto3.Session(profile_name=args.profile, region_name=args.region)

    account_id = session.client('sts').get_caller_identity().get('Account')

    if args.waf_acl:
        process_waf_acls(session, account_id, args.region, waf_acl_id=args.waf_acl)
    elif args.all:
        process_waf_acls(session, account_id, args.region, all_acls=True)
    else:
        print("Please specify either a specific WAF ACL ID or use the -a flag to process all ACLs.")

if __name__ == "__main__":
    main()
