#!/usr/bin/env python3

"""
[EC2.2] The VPC default security group should not allow inbound and outbound traffic

"""

import argparse
import boto3
from botocore.exceptions import ClientError

def main(profile, vpc_id):
    """
    main function
    """

    ec2 = boto3.client('ec2', profile_name=profile)

    try:
        response = ec2.describe_security_groups(
            Filters=[
                {
                    'Name': 'vpc-id',
                    'Values': [
                        vpc_id,
                    ]
                },
                {
                    'Name': 'group-name',
                    'Values': [
                        'default',
                    ]
                },
            ]
        )
    except ClientError as error:
        print(f"Error describing security groups: {error}")
        return

    if not response['SecurityGroups']:
        print("Error: default security group not found.")
        return

    group_id = response['SecurityGroups'][0]['GroupId']

    # Revoke all inbound rules
    try:
        ec2.revoke_security_group_ingress(
            GroupId=group_id,
            IpPermissions=response['SecurityGroups'][0]['IpPermissions']
        )
    except ClientError as error:
        print(f"Error revoking ingress rules: {error}")
        return

    # Revoke all outbound rules
    try:
        ec2.revoke_security_group_egress(
            GroupId=group_id,
            IpPermissions=response['SecurityGroups'][0]['IpPermissionsEgress']
        )
    except ClientError as error:
        print(f"Error revoking egress rules: {error}")
        return

    print(f"""Successfully changed default security group {group_id}
    to not allow inbound and outbound traffic.""")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=(
            'Change AWS VPC default security group '
            'to not allow inbound and outbound traffic.'
        )
    )
    parser.add_argument('--profile', required=True, help='Name of the AWS account profile')
    parser.add_argument('--vpc-id', required=True, help='ID of the VPC')
    args = parser.parse_args()

    main(args.profile, args.vpc_id)
