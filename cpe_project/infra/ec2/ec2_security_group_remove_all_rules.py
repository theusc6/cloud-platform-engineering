"""
Remediates: "[EC2.2] This AWS control checks that the default security group of a
VPC does not allow inbound or outbound traffic."

A Python script that uses Boto3 to remove all inbound and outbound security group rules
from a specified security group using the provided AWS SSO profile name and AWS region.

Usage:
    python remove_sg_rules.py --profile <profile_name> --sg_id <security_group_id>
"""

import argparse
import boto3

from botocore.exceptions import ClientError


def remove_sg_rules(ec2, sg_id):
    """
    Remove all inbound and outbound rules from the specified security group.
    """
    try:
        security_group = ec2.SecurityGroup(sg_id)

        # Remove all inbound rules
        for rule in security_group.ip_permissions:
            security_group.revoke_ingress(IpPermissions=[rule])

        # Remove all outbound rules
        for rule in security_group.ip_permissions_egress:
            security_group.revoke_egress(IpPermissions=[rule])

        print(f"Successfully removed all ingress & egress rules from security group: {sg_id}")

    except ClientError as client_error:
        print(f"Error removing rules from security group {sg_id}: {client_error}")

def main():
    """
    Parses command-line arguments for AWS SSO profile, region, and security group ID,
    creates a Boto3 session, then removes all rules from the specified security group.
    """
    parser = argparse.ArgumentParser(description="Remove rules from an AWS security group")
    parser.add_argument("-p","--profile", help="AWS SSO profile name", required=True)
    parser.add_argument("-r","--region", help="AWS region", default='us-west-2')
    parser.add_argument("--sg_id", help="AWS security group ID", required=True)
    args = parser.parse_args()

    session = boto3.Session(profile_name=args.profile, region_name=args.region)

    ec2 = session.resource('ec2')

    remove_sg_rules(ec2, args.sg_id)


if __name__ == "__main__":
    main()
