#!/usr/bin/env python3

"""
List all ec2 instance details in the MyOrg Webservers account


"""

import argparse
import os
import csv
import boto3

# Ensure a profile argument is passed in
parser = argparse.ArgumentParser(description='List EC2 instance details in the Webservers account.')
parser.add_argument('-p', '--profile', required=True, help='AWS profile name for SSO login')
parser.add_argument('-c', '--csv', type=str, help='Name of CSV file to write to')
args = parser.parse_args()

session = boto3.Session(profile_name=args.profile)

# List of AWS regions
regions = ['us-west-2', 'us-east-1', 'ap-southeast-1']

if args.csv and not os.path.isfile(args.csv):
    # Create a CSV file to write instance details
    with open(args.csv, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Instance ID', 'Instance Type', 'State', 'Private IP', 'Region'])

# Iterate over each region
for region in regions:
    print(f"\nInstances in region: {region}")

    # Create a Boto3 EC2 client for the specific region
    ec2_client = session.client('ec2', region_name=region)

    # Retrieve a list of all EC2 instances in the region
    response = ec2_client.describe_instances()

    # Extract the list of instances from the response
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append(instance)

    for instance in instances:
        instance_id = instance['InstanceId']
        instance_type = instance['InstanceType']
        state = instance['State']['Name']
        private_ip = instance['PrivateIpAddress']

        print(f"Instance ID: {instance_id}, "
            f"Type: {instance_type}, "
            f"State: {state}, "
            f"Private IP: {private_ip}")

        if args.csv:
            with open(args.csv, 'a', newline='', encoding='utf-8') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([instance_id, instance_type, state, private_ip, region])

if args.csv:
    print(f"\nEC2 instance details written to {args.csv} file.")
