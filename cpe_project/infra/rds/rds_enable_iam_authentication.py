'''
This script enables IAM authentication for a specified
RDS database instance.

This satisfies Security Hub control [RDS.1]: RDS databases
should have IAM authentication enabled.
'''
import argparse
import boto3
from botocore.exceptions import ClientError

def enable_iam_authentication(rds_client, db_instance_identifier):
    """
    Enables IAM authentication for the specified RDS database instance.
    """
    try:
        rds_client.modify_db_instance(
            DBInstanceIdentifier=db_instance_identifier,
            EnableIAMDatabaseAuthentication=True,
            ApplyImmediately=True
        )
        print(f"Success! Enabled IAM authentication for RDS instance: {db_instance_identifier}")
    except ClientError as error:
        print(f"An error occurred while enabling IAM authentication: "
              f"{error.response['Error']['Message']}")

def main():
    """
    Parses command-line arguments, establishes an AWS session,
    and enables IAM authentication for an RDS database instance.
    """
    parser = argparse.ArgumentParser(description="Enable IAM Authentication for RDS Database")
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('-d', '--dbinstance', required=True, type=str,
                        help='Identifier of the RDS database instance')
    parser.add_argument('-r', '--region', required=False, default="us-west-2", type=str,
                        help='AWS region where the RDS instance is located')

    args = parser.parse_args()

    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    rds_client = session.client('rds')

    enable_iam_authentication(rds_client, args.dbinstance)

if __name__ == "__main__":
    main()
