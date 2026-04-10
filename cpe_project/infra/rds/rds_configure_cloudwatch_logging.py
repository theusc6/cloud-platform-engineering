'''
This script enables the publishing of logs from a specified RDS
database instance to CloudWatch Logs.

Publishing RDS logs to CloudWatch Logs allows for real-time monitoring of
database activity, streamlined log management, and enhanced debugging capabilities.
'''
import argparse
import boto3
from botocore.exceptions import ClientError

def enable_rds_logs_to_cloudwatch(rds_client, db_instance_identifier):
    """
    Enables the specified log types for an RDS database instance to be published to CloudWatch Logs.
    """
    try:
        rds_client.modify_db_instance(
            DBInstanceIdentifier=db_instance_identifier,
            CloudwatchLogsExportConfiguration={
                'EnableLogTypes': [
                    "audit",
                    "error",
                    "general",
                    "slowquery"
                ]
            },
            ApplyImmediately=True  # Apply changes immediately
        )
        print(f"Success! Enabled publishing of all log types for RDS "
        f"instance {db_instance_identifier} to CloudWatch Logs.")
    except ClientError as error:
        print(f"An error occurred while enabling logs publishing to "
        f"CloudWatch: {error.response['Error']['Message']}")

def main():
    """
    Parses command-line arguments, establishes an AWS session,
    and enables publishing of RDS logs to CloudWatch Logs.
    """
    parser = argparse.ArgumentParser(description="Enable Publishing of RDS Logs to CloudWatch")
    parser.add_argument('-p', '--profile', required=True, type=str,
        help='AWS profile name for SSO login')
    parser.add_argument('-d', '--dbinstance', required=True, type=str,
        help='Identifier of the RDS database instance')
    parser.add_argument('-r', '--region', required=False, default="us-west-2", type=str,
        help='AWS region where the RDS instance is located')

    args = parser.parse_args()

    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    rds_client = session.client('rds')

    enable_rds_logs_to_cloudwatch(rds_client, args.dbinstance)

if __name__ == "__main__":
    main()
