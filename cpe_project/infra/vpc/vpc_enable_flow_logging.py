"""
This script enables VPC flow logging with specific settings for a given VPC.

Usage: python3 vpc_enable_flow_logging.py -p <profile_name> -r <region_name> -v <vpc_id>
"""
import argparse
import json
import time
import boto3
from botocore.exceptions import ClientError

def parse_args():
    """
    Parse command-line arguments passed to the script.
    """
    parser = argparse.ArgumentParser(
        description='Enable VPC flow logging with specific settings for a specific VPC.'
        )
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('-r', '--region', required=True, type=str,
                        help='AWS region where the VPC is located')
    parser.add_argument('-v', '--vpc', required=True, type=str,
                        help='VPC ID')
    return parser.parse_args()

def create_iam_role(session):
    """
    Creates an IAM role with specific policies and returns its ARN.

    Parameters:
    session (boto3.Session): An AWS session object created by Boto3.

    Returns:
    str: The ARN of the created IAM role.
    """
    iam_client = session.client('iam')

    role_name = 'role-myorg-vpc-flow-logger+prod-ops'
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": [
                        "vpc-flow-logs.amazonaws.com"
                    ]
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }

    try:
        create_role_response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role so that Flow logs can publish flow '
            'log data directly to Amazon CloudWatch. [Applicable to '
            'CloudWatch Logging only - not S3]',
            Tags=[
                {
                    'Key': 'Category',
                    'Value': 'Security'
                }
            ]
        )

        policy_arns = [
            'arn:aws:iam::aws:policy/CloudWatchLogsFullAccess',
        ]

        for policy_arn in policy_arns:
            iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn
            )
        print(f"Creating {role_name}...")
        time.sleep(10)
        print(f"The role {role_name} successfully created.")
        return create_role_response['Role']['Arn']


    except ClientError as client_error:
        if client_error.response['Error']['Code'] == 'EntityAlreadyExists':
            print(f"The IAM role {role_name} already exists.")
            role_arn = iam_client.get_role(RoleName=role_name)['Role']['Arn']
            return role_arn
        print(f"An error occurred while creating the IAM role: "
              f"{client_error.response['Error']['Message']}")
        return None


def create_s3_bucket(session, bucket_name, account_id, region):
    """
    This function creates an Amazon S3 bucket with a specified name, policy, tagging,
    versioning configuration, public access block configuration, and lifecycle policy.

    Parameters:
    session (boto3.Session): An AWS session object created by Boto3.
    bucket_name (str): The name of the S3 bucket to be created.
    account_id (str): The AWS account ID in which the S3 bucket will be created.
    region (str): The AWS region where the S3 bucket will be created.

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
            return  # Ensure to exit if bucket creation failed

    # Apply bucket policy
    try:
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )
        print(f"The bucket policy has been applied to {bucket_name}.")
    except ClientError as client_error:
        print(f"An error occurred while applying the bucket policy: "
        f"{client_error.response['Error']['Message']}")

    # Apply tags to the bucket
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

    if ('myorg-securityhub-s3.9accesslogging' not in bucket_name) or \
        ('myorg-securityhub-ec2.6flowlog' not in bucket_name):
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


def enable_vpc_flow_logging(params):
    """
    Enable VPC flow logging with specific settings for the given VPC ID.
    """
    flow_log_name = (
        f"myorg-securityhub-ec2.6flowlog-"
        f"{params['account_id']}-"
        f"{params['region']}-"
        f"{params['vpc_id']}"
       )
    s3_arn = f"arn:aws:s3:::{params['bucket_name']}/{params['vpc_id']}"

    try:
        response = params['ec2'].create_flow_logs(
            ResourceIds=[params['vpc_id']],
            ResourceType='VPC',
            TrafficType='ALL',
            LogDestinationType='s3',
            LogDestination=s3_arn,
            LogFormat='${version} ${account-id} ${interface-id} ${srcaddr} ${dstaddr} ${srcport} '
            '${dstport} ${protocol} ${packets} ${bytes} ${start} ${end} ${action} ${log-status}',
            MaxAggregationInterval=600,

            #Use the ARN of the IAM role that allows Amazon EC2 to publish flow
            # logs to a CloudWatch Logs log group in your account. The correct
            # variable to use is DeliverLogsPermissionArn=[]

            #This parameter is required if the destination type is cloud-watch-logs
            # and unsupported otherwise. This script uses S3.
        )

        if response['FlowLogIds']:
            params['ec2'].create_tags(
                Resources=response['FlowLogIds'],
                Tags=[
                    {
                        'Key': 'Category', 
                        'Value': 'Security'
                     },
                     {
                         'Key': 'Name',
                         'Value': flow_log_name
                     }
                    ]
            )
            print(f"Success! VPC flow logging is enabled for VPC '{params['vpc_id']}' "
                  f"with flow log name '{flow_log_name}'.")
        else:
            print(f"An error occurred: {response['Unsuccessful'][0]['Error']['Message']}")
    except ClientError as error:
        print(f"An error occurred: {error.response['Error']['Message']}")

def main():
    """
    Main function of the script.
    """
    args = parse_args()
    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    ec2 = session.client('ec2')

    sts = session.client('sts')
    account_id = sts.get_caller_identity().get('Account')

    iam_role_arn = create_iam_role(session)


    bucket_name = f'myorg-securityhub-ec2.6flowlogging-{account_id}-{args.region}'
    create_s3_bucket(session, bucket_name, account_id, args.region)

    params = {
        'ec2': ec2,
        'vpc_id': args.vpc,
        'bucket_name': bucket_name,
        'region': args.region,
        'account_id': account_id,
        'iam_role_arn': iam_role_arn,
    }

    enable_vpc_flow_logging(params)

if __name__ == "__main__":
    main()
