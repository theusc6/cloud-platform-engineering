'''
This script enables automatic minor version upgrades for a specified
RDS database instance.

Enabling automatic minor version upgrades ensures that your RDS database
instances are up-to-date with the latest minor version patches, improving
security and stability.
'''
import argparse
import boto3
from botocore.exceptions import ClientError

def enable_auto_minor_version_upgrade(rds_client, db_instance_identifier):
    """
    Enables automatic minor version upgrades for the specified RDS database instance.
    """
    try:
        rds_client.modify_db_instance(
            DBInstanceIdentifier=db_instance_identifier,
            AutoMinorVersionUpgrade=True,
            ApplyImmediately=True
        )
        print(f"Success! Enabled automatic minor version upgrades "
                f"for RDS instance: {db_instance_identifier}")
    except ClientError as error:
        print(f"An error occurred while enabling automatic minor "
                f"version upgrades: {error.response['Error']['Message']}")

def main():
    """
    Parses command-line arguments, establishes an AWS session,
    and enables automatic minor version upgrades for an RDS database instance.
    """
    parser = argparse.ArgumentParser(
        description="Enable Automatic MinorVersion Upgrades for RDS Database")
    parser.add_argument('-p', '--profile', required=True, type=str,
        help='AWS profile name for SSO login')
    parser.add_argument('-d', '--dbinstance', required=True, type=str,
        help='Identifier of the RDS database instance')
    parser.add_argument('-r', '--region', required=False, default="us-west-2", type=str,
        help='AWS region where the RDS instance is located')

    args = parser.parse_args()

    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    rds_client = session.client('rds')

    enable_auto_minor_version_upgrade(rds_client, args.dbinstance)

if __name__ == "__main__":
    main()
