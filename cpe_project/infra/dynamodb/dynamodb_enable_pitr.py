"""
This script enables point-in-time recovery for a specific DynamoDB table.

Usage: python3 enable_point_in_time_recovery.py
    --profile <profile_name>
    --table <table_name>
    --region <region_name>
"""
import argparse
import boto3
from botocore.exceptions import ClientError

def parse_args():
    """
    Parse command-line arguments passed to the script.
    """
    parser = argparse.ArgumentParser(
        description='Enable Point-In-Time Recovery for a DynamoDB Table.'
        )
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('-t', '--table', required=True, type=str,
                        help='DynamoDB table name')
    parser.add_argument('-r', '--region', default='us-west-2', type=str,
                        help='AWS region for the DynamoDB table')
    return parser.parse_args()

def enable_point_in_time_recovery(dynamodb, table_name):
    """
    Enable point-in-time recovery for the given DynamoDB table.
    """
    try:
        response = dynamodb.update_continuous_backups(
            TableName=table_name,
            PointInTimeRecoverySpecification={
                'PointInTimeRecoveryEnabled': True
            }
        )
        continuous_backup_desc = response['ContinuousBackupsDescription']
        point_in_time_recovery_desc = continuous_backup_desc['PointInTimeRecoveryDescription']
        status = point_in_time_recovery_desc['PointInTimeRecoveryStatus']
        print(f"Success! Point-in-time recovery status for table '{table_name}': {status}")
    except ClientError as error:
        print(f"An error occurred: {error.response['Error']['Message']}")

def main():
    """
    Main function of the script.
    """
    args = parse_args()
    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    dynamodb = session.client('dynamodb', region_name=args.region)

    enable_point_in_time_recovery(dynamodb, args.table)

if __name__ == "__main__":
    main()
