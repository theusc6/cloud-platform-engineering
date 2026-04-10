'''
This script configures an RDS database instance for high availability by enabling
the Multi-AZ deployment option.

Multi-AZ deployments provide enhanced availability and durability for RDS instances,
making them fault-tolerant to failure of a single component or an Availability Zone.
'''
import argparse
import boto3
from botocore.exceptions import ClientError

def enable_multi_az(rds_client, db_instance_identifier):
    """
    Configures the specified RDS database instance for high availability by enabling Multi-AZ.
    """
    try:
        rds_client.modify_db_instance(
            DBInstanceIdentifier=db_instance_identifier,
            MultiAZ=True,
            ApplyImmediately=True
        )
        print(f"Success! Configured RDS instance {db_instance_identifier} "
            f"for high availability (Multi-AZ).")
    except ClientError as error:
        print(f"An error occurred while configuring Multi-AZ: {error.response['Error']['Message']}")

def main():
    """
    Parses command-line arguments, establishes an AWS session,
    and configures an RDS database instance for high availability.
    """
    parser = argparse.ArgumentParser(description="Configure RDS Database "
            "Instance for High Availability (Multi-AZ)")
    parser.add_argument('-p', '--profile', required=True, type=str,
            help='AWS profile name for SSO login')
    parser.add_argument('-d', '--dbinstance', required=True, type=str,
            help='Identifier of the RDS database instance')
    parser.add_argument('-r', '--region', required=False, default="us-west-2", type=str,
            help='AWS region where the RDS instance is located')

    args = parser.parse_args()

    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    rds_client = session.client('rds')

    enable_multi_az(rds_client, args.dbinstance)

if __name__ == "__main__":
    main()
