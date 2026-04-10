'''
This script configures an RDS database instance to prohibit public access by setting
the PubliclyAccessible configuration to false.

Prohibiting public access to an RDS instance enhances security by ensuring that the 
database cannot be accessed from the internet.
'''
import argparse
import boto3
from botocore.exceptions import ClientError

def prohibit_public_access(rds_client, db_instance_identifier):
    """
    Configures the specified RDS database instance to prohibit public access.
    """
    try:
        rds_client.modify_db_instance(
            DBInstanceIdentifier=db_instance_identifier,
            PubliclyAccessible=False,
            ApplyImmediately=True  # Apply changes immediately
        )
        print(f"Success! Configured RDS instance {db_instance_identifier} to "
              f"prohibit public access.")
    except ClientError as error:
        print(f"An error occurred while setting the public accessibility: "
              f"{error.response['Error']['Message']}")

def main():
    """
    Parses command-line arguments, establishes an AWS session,
    and configures an RDS database instance to prohibit public access.
    """
    parser = argparse.ArgumentParser(description="Configure RDS Database "
                                     "Instance to Prohibit Public Access")
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('-d', '--dbinstance', required=True, type=str,
                        help='Identifier of the RDS database instance')
    parser.add_argument('-r', '--region', required=False, default="us-west-2", type=str,
                        help='AWS region where the RDS instance is located')

    args = parser.parse_args()

    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    rds_client = session.client('rds')

    prohibit_public_access(rds_client, args.dbinstance)

if __name__ == "__main__":
    main()
