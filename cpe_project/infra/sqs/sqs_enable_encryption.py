'''
This script enables server-side encryption for the specified
SQS queue.

This satisfies Security Hub control [SQS.1]: Amazon SQS queues
should be encrypted at rest
'''
import argparse
import boto3
from botocore.exceptions import ClientError

def enable_sqs_encryption(sqs_client, queue_url, queue_name):
    """
    Enables server-side encryption for the specified SQS queue.
    """
    try:
        encryption_attributes = {
            'KmsMasterKeyId': 'alias/aws/sqs',
            'SqsManagedSseEnabled': 'false'
        }
        sqs_client.set_queue_attributes(
            QueueUrl=queue_url,
            Attributes={
                'KmsMasterKeyId': encryption_attributes['KmsMasterKeyId'],
                'SqsManagedSseEnabled': encryption_attributes['SqsManagedSseEnabled']
            }
        )
        print(f"Success! Enabled server-side encryption for SQS queue: {queue_name}")
    except ClientError as error:
        print(f"An error occurred while enabling SQS encryption: "
              f"{error.response['Error']['Message']}")
def get_queue_url(sqs_client, queue_name):
    """
    Retrieves the URL of an SQS queue by its name.
    """
    try:
        response = sqs_client.get_queue_url(QueueName=queue_name)
        return response['QueueUrl']
    except ClientError as error:
        print(f"An error occurred while retrieving the queue URL: "
              f"{error.response['Error']['Message']}")
        return None

def main():
    """
    Parses command-line arguments, establishes an AWS session,
    and enables server-side encryption for an SQS queue.
    """
    parser = argparse.ArgumentParser(description="Enable SQS Queue Encryption")
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('-q', '--queue', required=True, type=str,
                        help='Name of the SQS queue')
    parser.add_argument('-r', '--region', required=False, default="us-west-2", type=str,
                        help='AWS region where the SQS queue is located')

    args = parser.parse_args()

    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    sqs_client = session.client('sqs')

    queue_url = get_queue_url(sqs_client, args.queue)
    if queue_url:
        enable_sqs_encryption(sqs_client, queue_url, args.queue)

if __name__ == "__main__":
    main()
