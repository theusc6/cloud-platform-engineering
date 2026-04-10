#!/usr/bin/env python3

"""
[ELB.6] This control checks whether an Application Load Balancer has deletion protection enabled.

"""

import argparse
import sys
import boto3
from botocore.exceptions import ClientError

# Ensure a profile argument is passed in
# parser = argparse.ArgumentParser(description='')
parser = argparse.ArgumentParser(
    description=(
        'Ensure the named AWS Application Load Balancer complies with '
        'the AWS Foundational Security Best Practices v1.0.0.'
    )
)
parser.add_argument('-n', '--name', required=True, help='Name of the AWS alb to apply changes')
parser.add_argument('-p', '--profile', required=True, help='AWS profile name for SSO login')
args = parser.parse_args()

# args
alb_name = args.name

# Set up boto3 client
session = boto3.Session(profile_name=args.profile)
elbv2_client = session.client('elbv2')

# Confirm load balancer exists
try:
    alb = elbv2_client.describe_load_balancers(Names=[alb_name])['LoadBalancers'][0]
    print(f'{alb_name}: Load balancer exists.')
except ClientError as error:
    if error.response['Error']['Code'] == 'LoadBalancerNotFound':
        print(f"Load balancer {alb_name} doesn't exist.")
        sys.exit()
    elif error.response['Error']['Code'] == 'AccessDeniedException':
        print(f"Access denied to load balancer {alb_name}.")
        sys.exit()
    else:
        raise

# Enable deletion protection
try:
    elbv2_client.modify_load_balancer_attributes(
        LoadBalancerArn=alb['LoadBalancerArn'],
        Attributes=[{
            'Key': 'deletion_protection.enabled',
            'Value': 'true'
        }]
    )
    print(f'{alb_name}: Deletion protection enabled.')
except ClientError as error:
    print(f"Failed to enable deletion protection: {error}")

# Set tags
try:
    elbv2_client.add_tags(
        ResourceArns=[
            alb['LoadBalancerArn']
        ],
        Tags=[
                {
                    'Key': 'Category',
                    'Value': 'NetOps'
                },
                {
                    'Key': 'Product',
                    'Value': 'Network'
                }
            ]
    )
    print(f'{alb_name}: Tagging enabled.')
except ClientError as error:
    print(f"Failed to set tags: {error}")
