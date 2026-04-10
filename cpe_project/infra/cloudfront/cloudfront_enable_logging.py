"""
This script enables CloudFront logging with specific settings for a given distribution.
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
        description='Enable CloudFront logging with specific settings for a specific distribution.'
    )
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('-r', '--region', required=True, type=str,
                        help='AWS region where the CloudFront distribution is located')
    parser.add_argument('-d', '--distribution', required=True, type=str,
                        help='CloudFront distribution ID')
    return parser.parse_args()

def get_canonical_id(session):
    """
    Retrieve the canonical ID of the AWS account.
    """
    s3_client = session.client('s3')
    response = s3_client.list_buckets()
    return response['Owner']['ID']

def create_bucket(s3_client, bucket_name, region):
    """
    Create an S3 bucket.
    """
    try:
        if region == 'us-east-1':
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        print(f"{bucket_name} has now been created.")
    except ClientError as client_error:
        if client_error.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print(f"Bucket {bucket_name} already exists.")
        else:
            print(f"An error occurred while creating the bucket: "
                  f"{client_error.response['Error']['Message']}")
            return False
    return True

def apply_bucket_policy(s3_client, bucket_name, bucket_policy):
    """
    Apply a policy to the S3 bucket.
    """
    try:
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )
        print(f"The bucket policy has been applied to {bucket_name}.")
    except ClientError as client_error:
        print(f"An error occurred while applying the bucket policy: "
              f"{client_error.response['Error']['Message']}")

def apply_bucket_tags(s3_client, bucket_name):
    """
    Apply tags to the S3 bucket.
    """
    try:
        s3_client.put_bucket_tagging(
            Bucket=bucket_name,
            Tagging={'TagSet': [{'Key': 'Category', 'Value': 'Security'}]}
        )
        print(f"Tags have been applied to bucket {bucket_name}.")
    except ClientError as client_error:
        print(f"An error occurred while applying bucket tags: "
              f"{client_error.response['Error']['Message']}")

def enable_bucket_versioning(s3_client, bucket_name):
    """
    Enable versioning on the S3 bucket.
    """
    try:
        s3_client.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={
                'Status': 'Enabled'
            }
        )
        print(f"Versioning is enabled for {bucket_name}.")
    except ClientError as client_error:
        print(f"An error occurred while enabling bucket versioning: "
              f"{client_error.response['Error']['Message']}")

def block_public_access(s3_client, bucket_name):
    """
    Block public access to the S3 bucket.
    """
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

def apply_lifecycle_policy(s3_client, bucket_name, lifecycle_policy):
    """
    Apply a lifecycle policy to the S3 bucket.
    """
    try:
        s3_client.put_bucket_lifecycle_configuration(
            Bucket=bucket_name,
            LifecycleConfiguration=lifecycle_policy
        )
        print(f"Applied bucket lifecycle policy for bucket {bucket_name}.")
    except ClientError as client_error:
        print(f"An error occurred while applying lifecycle policy: "
              f"{client_error.response['Error']['Message']}")

def set_bucket_ownership_controls(s3_client, bucket_name):
    """
    Set ownership controls for the S3 bucket.
    """
    try:
        s3_client.put_bucket_ownership_controls(
            Bucket=bucket_name,
            OwnershipControls={
                'Rules': [
                    {
                        'ObjectOwnership': 'BucketOwnerPreferred'
                    }
                ]
            }
        )
        print(f"Bucket ownership controls set to Object Writer for {bucket_name}.")
    except ClientError as client_error:
        print(f"An error occurred while setting bucket ownership controls: "
              f"{client_error.response['Error']['Message']}")

def set_bucket_acl(s3_client, bucket_name, canonical_id):
    """
    Set ACLs for the S3 bucket to allow CloudFront logging.
    """
    try:
        s3_client.put_bucket_acl(
            Bucket=bucket_name,
            AccessControlPolicy={
                'Grants': [
                    {
                        'Grantee': {
                            'Type': 'CanonicalUser',
                            'ID': 'c4c1ede66af53448b93c283ce9448c4ba468c9432aa01d700d3878632f77d2d0'
                        },
                        'Permission': 'FULL_CONTROL'
                    }
                ],
                'Owner': {
                    'ID': canonical_id
                }
            }
        )
        print(f"ACL 'log-delivery-write' is set for bucket {bucket_name}.")
    except ClientError as client_error:
        print(f"An error occurred while setting bucket ACL: "
              f"{client_error.response['Error']['Message']}")

def enable_bucket_logging(s3_client, bucket_name, log_bucket_name):
    """
    Enable logging for the S3 bucket.
    """
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

def create_s3_bucket(session, bucket_name, canonical_id, account_id, region):
    """
    This function creates an Amazon S3 bucket with a specified name, policy, tagging,
    versioning configuration, public access block configuration, lifecycle policy,
    and sets the bucket ownership to Object Writer.
    """
    s3_client = session.client('s3')

    if not create_bucket(s3_client, bucket_name, region):
        return

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
                "Resource": f"arn:aws:s3:::{bucket_name}/*",
                "Condition": {
                    "StringEquals": {
                        "aws:SourceAccount": account_id,
                        "s3:x-amz-acl": "bucket-owner-full-control"
                    },
                    "ArnLike": {
                        "aws:SourceArn": f"arn:aws:logs:{region}:{account_id}:*"
                    }
                }
            },
            {
                "Sid": "AWSLogDeliveryAclCheck",
                "Effect": "Allow",
                "Principal": {
                    "Service": "delivery.logs.amazonaws.com"
                },
                "Action": [
                    "s3:GetBucketAcl",
                    "s3:ListBucket"
                ],
                "Resource": f"arn:aws:s3:::{bucket_name}",
                "Condition": {
                    "StringEquals": {
                        "aws:SourceAccount": account_id
                    },
                    "ArnLike": {
                        "aws:SourceArn": f"arn:aws:logs:{region}:{account_id}:*"
                    }
                }
            },
            {
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
            }
        ]
    }

    apply_bucket_policy(s3_client, bucket_name, bucket_policy)
    apply_bucket_tags(s3_client, bucket_name)
    enable_bucket_versioning(s3_client, bucket_name)
    block_public_access(s3_client, bucket_name)

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
                    'NewerNoncurrentVersions': 1
                },
                'AbortIncompleteMultipartUpload': {
                    'DaysAfterInitiation': 7
                }
            }
        ]
    }

    apply_lifecycle_policy(s3_client, bucket_name, lifecycle_policy)
    set_bucket_ownership_controls(s3_client, bucket_name)
    set_bucket_acl(s3_client, bucket_name, canonical_id)

    log_bucket_name = f"myorg-securityhub-s3.9accesslogging-{account_id}-{region}"
    enable_bucket_logging(s3_client, bucket_name, log_bucket_name)

def enable_cloudfront_logging(params):
    """
    Enable CloudFront logging with specific settings for the given distribution ID.
    """
    cloudfront = params['cloudfront']
    distribution_id = params['distribution_id']
    bucket_name = params['bucket_name']

    try:
        response = cloudfront.get_distribution_config(Id=distribution_id)
        distribution_config = response['DistributionConfig']
        etag = response['ETag']

        distribution_config['Logging'] = {
            'Enabled': True,
            'IncludeCookies': True,
            'Bucket': f"{bucket_name}.s3.amazonaws.com",
            'Prefix': f"{distribution_id}/"
        }

        cloudfront.update_distribution(
            Id=distribution_id,
            DistributionConfig=distribution_config,
            IfMatch=etag
        )

        print(f"Success! CloudFront logging is enabled for distribution '{distribution_id}' "
              f"with logs being sent to bucket '{bucket_name}' with prefix '{distribution_id}/'.")
    except ClientError as error:
        print(f"An error occurred: {error.response['Error']['Message']}")

def main():
    """
    Main function of the script.
    """
    args = parse_args()
    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    cloudfront = session.client('cloudfront')

    canonical_id = get_canonical_id(session)

    sts = session.client('sts')
    account_id = sts.get_caller_identity().get('Account')

    bucket_name = f'myorg-securityhub-cloudfront.5logging-{account_id}-{args.region}'
    create_s3_bucket(session, bucket_name, canonical_id, account_id, args.region)

    params = {
        'cloudfront': cloudfront,
        'distribution_id': args.distribution,
        'bucket_name': bucket_name,
        'region': args.region,
        'account_id': str(account_id)
    }

    enable_cloudfront_logging(params)

if __name__ == "__main__":
    main()
