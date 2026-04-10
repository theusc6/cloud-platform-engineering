#!/usr/bin/env python3

"""
Create an AWS FSx file system and share it with the specified CIDR block.
"""

import argparse
import ipaddress
import boto3
from botocore.exceptions import ClientError

def create_fsx_share(vpc_id, subnet_id, allowed_cidr, profile):
    """
    Create an AWS FSx file system and share it with the specified CIDR block.
    """
    try:
        ipaddress.ip_network(allowed_cidr)
    except ValueError as error:
        print(f"Error: Invalid CIDR block - {error}")
        return

    fsx = boto3.Session(profile_name=profile)
    fsx = fsx.client('fsx')

    # Create the security group for the FSx file system
    sg_name = 'FSxSecurityGroup'
    sg_description = 'Security group for FSx file system'
    sg_response = fsx.client('ec2').create_security_group(
        GroupName=sg_name,
        Description=sg_description,
        VpcId=vpc_id
    )

    if sg_response['ResponseMetadata']['HTTPStatusCode'] != 200:
        print(f"Error creating security group: {sg_response}")
        return

    security_group_id = sg_response['GroupId']

    # Allow inbound traffic from the specified CIDR block to the security group
    sg_ingress_response = fsx.client('ec2').authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 139,
                'ToPort': 139,
                'IpRanges': [
                    {
                        'CidrIp': allowed_cidr,
                        'Description': 'Access to FSx file system from specified CIDR'
                    }
                ]
            },
            {
                'IpProtocol': 'tcp',
                'FromPort': 445,
                'ToPort': 445,
                'IpRanges': [
                    {
                        'CidrIp': allowed_cidr,
                        'Description': 'Access to FSx file system from specified CIDR'
                    }
                ]
            }
        ]
    )

    if sg_ingress_response['ResponseMetadata']['HTTPStatusCode'] != 200:
        print(f"Error adding ingress rule to security group: {sg_ingress_response}")
        # delete the security group to avoid orphaned resources
        fsx.client('ec2').delete_security_group(GroupId=security_group_id)
        return

    # Create the FSx file system
    fsx_response = fsx.create_file_system(
        FileSystemType='WINDOWS',
        StorageCapacity=3000,
        ThroughputCapacity=50,
        SubnetIds=[subnet_id],
        SecurityGroupIds=[security_group_id],
        BackupId='NONE'
    )

    if fsx_response['ResponseMetadata']['HTTPStatusCode'] != 200:
        print(f"Error creating file system: {fsx_response}")
        # delete the security group and file system to avoid orphaned resources
        fsx.client('ec2').delete_security_group(GroupId=security_group_id)
        fsx.delete_file_system(FileSystemId=fsx_response['FileSystem']['FileSystemId'])
        return

    # Wait for the file system to be available
    file_system_id = fsx_response['FileSystem']['FileSystemId']
    waiter = fsx.get_waiter('file_system_available')
    try:
        waiter.wait(FileSystemIds=[file_system_id])
    except ClientError as error:
        print(f"Error waiting for file system to be available: {error}")
        # delete the security group and file system to avoid orphaned resources
        fsx.client('ec2').delete_security_group(GroupId=security_group_id)
        fsx.delete_file_system(FileSystemId=file_system_id)
        return

    # Create the file share
    file_share_response = fsx.create_smb_file_share(
        FileSystemId=file_system_id,
        Name='FSxShare',
        Authentication='ActiveDirectory',
        Tags=[
            {
                'Key': 'Name',
                'Value': 'FSxShare'
            }
        ],
        ActiveDirectoryConfiguration={
            'UserName': 'USERNAME',
            'Password': 'PASSWORD',
            'DomainName': 'DOMAIN_NAME',
            'OrganizationalUnitDistinguishedName': 'OU_DISTINGUISHED_NAME',
            'FileSystemAdministratorsGroup': 'FILESYSTEM_ADMINS_GROUP_NAME'
        }
    )

    # Print the output
    print('FSx file share created successfully')
    print(f"File share name: {file_share_response['Name']}")
    print(f"File share ARN: {file_share_response['FileShareARN']}")
    print(f"Security group ID: {security_group_id}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Create a Windows FSx file share that is only open to specific subnets')
    parser.add_argument('-v', '--vpc-id', type=str, required=True,
                        help='The ID of the VPC where the FSx file system will be created')
    parser.add_argument('-s', '--subnet-id', type=str, required=True,
                        help='The ID of the subnet where the FSx file system will be created')
    parser.add_argument('-a', '--allowed-cidr', type=str, required=True,
                        help='The CIDR block that is allowed to access the FSx file system')
    parser.add_argument('-p', '--profile', type=str, required=True,
                        help='The name of the AWS profile for authentication')

    args = parser.parse_args()
