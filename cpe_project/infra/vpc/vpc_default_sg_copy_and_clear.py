"""
Copy the a VPC Security Group and clear all rules from the copied Security Group.
"""

import argparse
import logging
import boto3

from botocore.exceptions import ClientError

def filter_existing_rules(new_permissions, existing_permissions):
    """
    Filter out rules that already exist in the security group.
    """
    filtered_permissions = []
    for new_permission in new_permissions:
        if new_permission not in existing_permissions:
            filtered_permissions.append(new_permission)
    return filtered_permissions

def copy_and_clear_default_security_group(ec2, sg_id):
    """
    Copy the specified security group and remove all inbound and outbound rules from the original group.
    """
    try:
        # Get the specified security group
        original_security_group = ec2.SecurityGroup(sg_id)

        # Create a copy of the specified security group
        copied_security_group = ec2.create_security_group(
            GroupName='DefaultSGCopy',
            Description='Copy of Default VPC Security Group',
            VpcId=original_security_group.vpc_id
        )

        # Copy all inbound and outbound rules from the original security group to the copied security group
        existing_ingress_permissions = copied_security_group.ip_permissions
        new_ingress_permissions = original_security_group.ip_permissions
        filtered_ingress_permissions = filter_existing_rules(new_ingress_permissions, existing_ingress_permissions)

        if filtered_ingress_permissions:
            copied_security_group.authorize_ingress(IpPermissions=filtered_ingress_permissions)

        if original_security_group.ip_permissions_egress:
            existing_egress_permissions = copied_security_group.ip_permissions_egress
            new_egress_permissions = original_security_group.ip_permissions_egress
            filtered_egress_permissions = filter_existing_rules(new_egress_permissions, existing_egress_permissions)

            if filtered_egress_permissions:
                copied_security_group.authorize_egress(IpPermissions=filtered_egress_permissions)

        # Add tags to the copied security group
        tags = [
            {
                'Key': 'Category',
                'Value': 'CPE'
            },
            {
                'Key': 'Product',
                'Value': 'Default VPC Security Group'
            },
            {
                'Key': 'Name',
                'Value': 'new-default-sg'
            }
        ]
        copied_security_group.create_tags(Tags=tags)

        # Remove all inbound and outbound rules from the original security group
        if original_security_group.ip_permissions:
            original_security_group.revoke_ingress(IpPermissions=original_security_group.ip_permissions)
        if original_security_group.ip_permissions_egress:
            original_security_group.revoke_egress(IpPermissions=original_security_group.ip_permissions_egress)

        logging.info(
            "Successfully created a copy of security group '%s', added tags, and cleared all rules from the original security group.",
            sg_id
        )

    except ClientError as client_error:
        logging.error(
            "Error copying and clearing rules from security group %s: %s",
            sg_id,
            client_error.response['Error']['Message']
        )

def main():
    """
    Parses command-line arguments for AWS SSO profile, region, and security group ID,
    creates a Boto3 session, then copies and clears all rules from the specified security group.
    """
    parser = argparse.ArgumentParser(description="Copy and clear a specified AWS security group")
    parser.add_argument("-p", "--profile", help="AWS SSO profile name", required=True)
    parser.add_argument("-r", "--region", help="AWS region", default='us-west-2')
    parser.add_argument("--sg_id", help="AWS security group ID", required=True)
    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    ec2 = session.resource('ec2')

    copy_and_clear_default_security_group(ec2, args.sg_id)

if __name__ == "__main__":
    main()
