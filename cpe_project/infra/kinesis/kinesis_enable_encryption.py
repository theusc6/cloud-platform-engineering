'''
This script enables server-side encryption for specified
Kinesis streams.

This satisfies Security Hub control [Kinesis.1]: Kinesis streams
should be encrypted at rest
'''
import argparse
import boto3
from botocore.exceptions import ClientError

def enable_kinesis_encryption(kinesis_client, stream_name):
    """
    Enables server-side encryption for the specified Kinesis stream.
    """
    try:
        kinesis_client.start_stream_encryption(
            StreamName=stream_name,
            EncryptionType='KMS',
            KeyId='alias/aws/kinesis'
        )
        print(f"Success! Enabled server-side encryption for Kinesis stream: {stream_name}")
    except ClientError as error:
        print(f"An error occurred while enabling Kinesis encryption: "
              f"{error.response['Error']['Message']}")

def main():
    """
    Parses command-line arguments, establishes an AWS session,
    and enables server-side encryption for a Kinesis stream.
    """
    parser = argparse.ArgumentParser(description="Enable Kinesis Stream Encryption")
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('-s', '--stream', required=True, type=str,
                        help='Name of the Kinesis stream')
    parser.add_argument('-r', '--region', required=False, default="us-west-2", type=str,
                        help='AWS region where the Kinesis stream is located')

    args = parser.parse_args()

    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    kinesis_client = session.client('kinesis')

    enable_kinesis_encryption(kinesis_client, args.stream)

if __name__ == "__main__":
    main()
