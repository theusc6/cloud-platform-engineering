'''
This script enables deletion protection for a specified
DynamoDB table.

Enabling deletion protection helps prevent the table from being
accidentally deleted.
'''
import argparse
import boto3
from botocore.exceptions import ClientError

def enable_dynamodb_deletion_protection(dynamodb_client, table_name):
    """
    Enables deletion protection for the specified DynamoDB table.
    """
    try:
        dynamodb_client.update_table(
            TableName=table_name,
            DeletionProtectionEnabled=True
        )
        print(f"Success! Enabled deletion protection for DynamoDB table: {table_name}")
    except ClientError as error:
        print(f"An error occurred while enabling deletion protection: "
              f"{error.response['Error']['Message']}")

def main():
    """
    Parses command-line arguments, establishes an AWS session,
    and enables deletion protection for a DynamoDB table.
    """
    parser = argparse.ArgumentParser(description="Enable Deletion Protection for DynamoDB Table")
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('-t', '--tablename', required=True, type=str,
                        help='Name of the DynamoDB table')
    parser.add_argument('--region', required=False, default="us-west-2", type=str,
                        help='AWS region where the DynamoDB table is located')

    args = parser.parse_args()

    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    dynamodb_client = session.client('dynamodb')

    enable_dynamodb_deletion_protection(dynamodb_client, args.tablename)

if __name__ == "__main__":
    main()
