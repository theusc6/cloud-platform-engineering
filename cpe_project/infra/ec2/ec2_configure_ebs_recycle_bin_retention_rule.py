"""
This module provides functionality to create an Amazon Elastic Block Store (EBS)
recycle bin retention rule.
"""

import argparse
import boto3
from botocore.exceptions import ClientError

def create_ebs_recycle_bin_rule(rbin_client, rule_name, retention_period):
    """
    Creates an EBS recycle bin retention rule.
    """
    try:
        rbin_client.create_rule(
            Tags=[
            {
                'Key': 'Name',
                'Value': rule_name
            }],
            RetentionPeriod={
                'RetentionPeriodValue': retention_period,
                'RetentionPeriodUnit': 'DAYS'
            },
            Description= "Retain deleted snapshots for (3) days prior to "
            "permanent deletion.",
            ResourceType='EBS_SNAPSHOT'
        )
        print(f"Success! Created EBS recycle bin rule: {rule_name}")
    except ClientError as error:
        print(f"An error occurred while creating the recycle bin rule: "
              f"{error.response['Error']['Message']}")

def main():
    """
    Parses command-line arguments, establishes an AWS session,
    and creates an EBS recycle bin retention rule.
    """
    parser = argparse.ArgumentParser(description="Create EBS Recycle Bin Retention Rule")
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('-n', '--rulename', required=True, type=str,
                        help='Name of the EBS recycle bin rule')
    parser.add_argument('-t', '--retention', required=True, type=int,
                        help='Retention period in days for the EBS snapshots')
    parser.add_argument('-r', '--region', required=False, default="us-west-2", type=str,
                        help='AWS region where to create the rule')

    args = parser.parse_args()

    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    rbin_client = session.client('rbin')

    create_ebs_recycle_bin_rule(rbin_client, args.rulename, args.retention)

if __name__ == "__main__":
    main()
