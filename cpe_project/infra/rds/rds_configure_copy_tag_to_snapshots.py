'''
This script configures specified RDS database instances to automatically
copy all tags from the database instance to snapshots upon their creation.

This action aligns with best practices for resource management and
simplifies the identification and management of RDS snapshots.
'''
import argparse
import boto3
from botocore.exceptions import ClientError

def enable_copy_tags_to_snapshot(rds_client, db_instance_identifier):
    """
    Configures the specified RDS database instance to copy tags to snapshots.
    """
    try:
        rds_client.modify_db_instance(
            DBInstanceIdentifier=db_instance_identifier,
            CopyTagsToSnapshot=True,
            ApplyImmediately=True
        )
        print(f"Success! Configured RDS instance {db_instance_identifier}"
              f" to copy tags to snapshots.")
    except ClientError as error:
        print(f"An error occurred while setting the copy tags to snapshot option: "
              f"{error.response['Error']['Message']}")

def main():
    """
    Parses command-line arguments, establishes an AWS session,
    and configures RDS database instances to copy tags to snapshots.
    """
    parser = argparse.ArgumentParser(description="Configure RDS Instances "
                                    "to Copy Tags to Snapshots")
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('-d', '--dbinstance', required=True, type=str,
                        help='Identifier of the RDS database instance')
    parser.add_argument('-r', '--region', required=False, default="us-west-2", type=str,
                        help='AWS region where the RDS instance is located')

    args = parser.parse_args()

    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    rds_client = session.client('rds')

    enable_copy_tags_to_snapshot(rds_client, args.dbinstance)

if __name__ == "__main__":
    main()
