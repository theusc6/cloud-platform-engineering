"""
Remediates findings for:
"ELB.5	Application and Classic Load Balancers logging should be enabled"

This script enables access logging for all AWS ELB v2 in an account, 
creating an S3 bucket for each ELB. The S3 buckets have a specified 
name, policy, tagging, versioning configuration, public access block 
configuration, and lifecycle policy. The script allows the user to 
specify the AWS profile, region, and account ID.

Usage: python3 elb_v2_logging.py --profile <profile_name> --region <region> --all 
       python3 elb_v2_logging.py --profile <profile_name> --region <region> 
                                                          --load_balancer <lb name>

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
        description='Configure Access Logging for AWS ELB v2.'
        )
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('-r', '--region', default='us-west-2', type=str,
                        help='AWS region (default: us-west-2)')
    parser.add_argument('-lb', '--load_balancer', required=False, type=str,
                        help='Name of a single load balancer for access logging')
    parser.add_argument('-a', '--all', required=False, action='store_true',
                        help='Enable access logging for all load balancers')
    return parser.parse_args()

def create_s3_bucket(session, bucket_details):
    """
    This function creates an Amazon S3 bucket with a specified name, policy, tagging,
    versioning configuration, public access block configuration, and lifecycle policy.

    Parameters:
    session (boto3.Session): An AWS session object created by Boto3.
    bucket_details (dict): The details of the S3 bucket to be created.

    Returns:
    None
    """
    bucket_name = bucket_details["bucket_name"]
    account_id = bucket_details["account_id"]
    region = bucket_details["region"]

    s3_client = session.client('s3')

    #The below mapping is provided by AWS here:
    #https://docs.aws.amazon.com/elasticloadbalancing/latest/application/enable-access-logging.html
    region_account_mapping = {
        'us-east-1': '127311923021',
        'us-east-2': '033677994240',
        'us-west-1': '027434742980',
        'us-west-2': '797873946194',
        'af-south-1': '098369216593',
        'ap-east-1': '754344448648',
        'ap-southeast-1': '114774131450',
        'ap-southeast-2': '783225319266',
        'ap-south-1': '718504428378',
        'ap-northeast-2': '600734575887',
        'ap-northeast-1': '123456789012',
        'ca-central-1': '985666609251',
        'eu-central-1': '054676820928',
        'eu-west-1': '156460612806',
        'eu-west-2': '652711504416',
        'eu-south-1': '635631232127',
        'eu-west-3': '009996457667',
        'eu-north-1': '897822967062',
        'me-south-1': '076674570225',
        'sa-east-1': '507241528517',
        'ap-northeast-3': '383597477331',
        'ap-southeast-3': '589379963580',
    }

    elb_account_id = region_account_mapping[region]

    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": f"arn:aws:iam::{elb_account_id}:root"
                },
                "Action": "s3:PutObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*/AWSLogs/{account_id}/*"
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
            s3_client.create_bucket(
                Bucket=bucket_name
            )
        else:
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

def enable_logging(elbv2_client, session, lb_details):
    """
    Enable access logging for the given ELB v2.
    """
    load_balancer_arn = lb_details["load_balancer_arn"]
    bucket_name = lb_details["bucket_name"]
    prefix = lb_details["prefix"]
    account_id = lb_details["account_id"]
    region = lb_details["region"]

    print(f"Enabling logging for Load Balancer: {load_balancer_arn}")
    print(f"Bucket for logging: {bucket_name}")
    print(f"Prefix for logs: {prefix}")

    try:
        create_s3_bucket(session, {"bucket_name": bucket_name, "account_id": account_id,
                                   "prefix": prefix, "region": region})
    except ClientError as client_error:
        if client_error.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print(f"Bucket {bucket_name} already exists. Continuing with this bucket.")
        else:
            print(f"An error occurred when creating the bucket: "
                  f"{client_error.response['Error']['Message']}")
            return  # return from the function if an error other than
                    # BucketAlreadyOwnedByYou occurred

    try:
        s3_client = session.client('s3')
        while True:
            try:
                s3_client.head_bucket(Bucket=bucket_name)
                print(f"Bucket {bucket_name} is available.")
                break  # if no exception, the bucket exists, break the loop
            except ClientError:
                print("Bucket not yet available. Waiting...")
                time.sleep(5)  # sleep for 5 seconds before checking again

        print("Modifying load balancer attributes...")
        # disable logging
        elbv2_client.modify_load_balancer_attributes(
            LoadBalancerArn=load_balancer_arn,
            Attributes=[
                {
                    'Key': 'access_logs.s3.enabled',
                    'Value': 'false'
                },
            ]
        )
        # enable logging with new settings
        elbv2_client.modify_load_balancer_attributes(
            LoadBalancerArn=load_balancer_arn,
            Attributes=[
                {
                    'Key': 'access_logs.s3.enabled',
                    'Value': 'true'
                },
                {
                    'Key': 'access_logs.s3.bucket',
                    'Value': bucket_name
                },
                {
                    'Key': 'access_logs.s3.prefix',
                    'Value': prefix
                }
            ]
        )
        print("Success! Load balancer attributes modified.")
        print(f"Logging has been enabled for ELB '{load_balancer_arn}'.")
    except ClientError as error:
        print(f"An error occurred: {error.response['Error']['Message']}")

def process_load_balancers(elbv2_client, load_balancer_params):
    """
    Loop through all the Load Balancers and enable access logging.
    If a load balancer name is provided, only enable access logging for that one.
    """
    session = load_balancer_params['session']
    bucket_name = load_balancer_params['bucket_name']
    account_id = load_balancer_params['account_id']
    region = load_balancer_params['region']
    load_balancer_name = load_balancer_params.get('load_balancer_name', None)
    try:
        response = elbv2_client.describe_load_balancers()
        if not response['LoadBalancers']:
            print('No load balancers found.')
        for load_balancer in response['LoadBalancers']:
            print(f'Processing load balancer: {load_balancer["LoadBalancerName"]}')
            if load_balancer_name and load_balancer_name != load_balancer['LoadBalancerName']:
                continue
            load_balancer_arn = load_balancer['LoadBalancerArn']
            prefix = load_balancer['LoadBalancerName']
            enable_logging(elbv2_client, session, {"load_balancer_arn": load_balancer_arn,
                                                   "bucket_name": bucket_name, 
                                                   "prefix": prefix, 
                                                   "account_id": account_id,
                                                   "region": region})
    except ClientError as error:
        print(f"An error occurred: {error.response['Error']['Message']}")

def main():
    """
    Main function of the script.
    """
    args = parse_args()
    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    elbv2_client = session.client('elbv2')

    # get the account_id from the current session
    account_id = session.client('sts').get_caller_identity().get('Account')

    # form the bucket name based on the account_id and region
    bucket_name = f"myorg-securityhub-elb.5accesslogging-{account_id}-{args.region}"

    load_balancer_params = {
    'session': session, 
    'bucket_name': bucket_name, 
    'account_id': account_id,
    'region': args.region, 
    'load_balancer_name': args.load_balancer  # This can be omitted if None
}

    process_load_balancers(elbv2_client, load_balancer_params)

if __name__ == "__main__":
    main()
