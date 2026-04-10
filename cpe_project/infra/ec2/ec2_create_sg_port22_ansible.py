#!/usr/bin/env python3

"""
Create a default security group for Ansible access

"""

import argparse
import boto3
from botocore.exceptions import ClientError

# Ensure a profile argument is passed in
parser = argparse.ArgumentParser(description='Create default Ansible Security Group')
parser.add_argument('-p', '--profile', required=True, help='AWS profile name for SSO login')
args = parser.parse_args()

# Create a session using the specified profile
session = boto3.Session(profile_name=args.profile)

# Create an EC2 client object using the session
ec2_client = session.client('ec2')

# Get all VPCs
vpcs = ec2_client.describe_vpcs()

# Dictionary to store VPCs and the number of instances
vpcs_with_instances = {}

# Loop over each VPC
for vpc in vpcs['Vpcs']:
    # Get all instances in the VPC
    instances = ec2_client.describe_instances(
        Filters=[{'Name': 'vpc-id', 'Values': [vpc['VpcId']]}]
    )

    # Count the number of instances in the VPC
    instance_count = sum(len(reservation['Instances']) for reservation in instances['Reservations'])

    # Add the VPC and the number of instances to the dictionary
    vpcs_with_instances[vpc['VpcId']] = instance_count

# Print the VPCs and the number of instances
print(f"\nFound the following VPCs in {args.profile}:")

for vpc_id, count in vpcs_with_instances.items():
    print('VPC ID:', vpc_id, 'Number of instances:', count)

# Prompt the user to continue
user_input = input(
    "\nDo you want to create the security group in the VPCs that have instances? [Y/n]: "
    )

# Check if the user input is not 'n' or 'N'
if user_input.lower() != 'n':
    # Dictionary to store VPCs where the security group was added and the number of instances
    vpcs_with_sg = {}

    # Loop over each VPC
    for vpc_id, count in vpcs_with_instances.items():
        # Check if the VPC contains instances
        if count > 0:
            # Create the security group in the VPC
            try:
                response = ec2_client.create_security_group(
                    GroupName='ssh-rfc-1819',
                    Description='Security group for Ansible access',
                    VpcId=vpc_id
                )
                security_group_id = response['GroupId']
                print('Security group created with id', security_group_id, 'in VPC', vpc_id)

                data = ec2_client.authorize_security_group_ingress(
                    GroupId=security_group_id,
                    IpPermissions=[
                        {'IpProtocol': 'tcp',
                         'FromPort': 22,
                         'ToPort': 22,
                         'IpRanges': [{'CidrIp': '172.16.0.0/12'},
                                      {'CidrIp': '10.0.0.0/8'},
                                      {'CidrIp': '192.168.0.0/16'}]}
                    ])
                print('Ingress successfully set', data)

                # Add the VPC and the number of instances to the dictionary
                vpcs_with_sg[vpc_id] = count

            except ClientError as e:
                print(e)

    # Print the VPCs where the security group was added and the number of instances
    print("\nThe security group was added to the following VPCs:")
    for vpc_id, count in vpcs_with_sg.items():
        print('VPC ID:', vpc_id, 'Number of instances:', count)
else:
    print("Cancelled, no security groups were created.\n")
