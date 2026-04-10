'''
This script enables deletion protection for a specified
RDS database instance.

This action helps in safeguarding RDS databases from accidental
deletion, aligning with best practices for data protection and
disaster recovery.
'''
import argparse
import boto3
from botocore.exceptions import ClientError

def enable_deletion_protection(rds_client, db_instance_identifier):
    """
    Enables deletion protection for the specified RDS database instance.
    """
    try:
        rds_client.modify_db_instance(
            DBInstanceIdentifier=db_instance_identifier,
            DeletionProtection=True,
            ApplyImmediately=True
        )
        print(f"Success! Enabled deletion protection for RDS instance: {db_instance_identifier}")
    except ClientError as error:
        print(f"An error occurred while enabling deletion protection: "
              f"{error.response['Error']['Message']}")

def main():
    """
    Parses command-line arguments, establishes an AWS session,
    and enables deletion protection for an RDS database instance.
    """
    parser = argparse.ArgumentParser(description="Enable Deletion Protection for RDS Database")
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('-d', '--dbinstance', required=True, type=str,
                        help='Identifier of the RDS database instance')
    parser.add_argument('-r', '--region', required=False, default="us-west-2", type=str,
                        help='AWS region where the RDS instance is located')

    args = parser.parse_args()

    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    rds_client = session.client('rds')

    enable_deletion_protection(rds_client, args.dbinstance)

if __name__ == "__main__":
    main()
