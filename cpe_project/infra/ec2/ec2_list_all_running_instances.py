#!/usr/bin/env python3

"""
List all running ec2 instances from the audit account

"""

import argparse
import boto3

def get_account_id(profile_name):
    """
    Retrieve the AWS account ID associated with the given profile name
    """
    session = boto3.Session(profile_name=profile_name)
    sts_client = session.client('sts')
    response = sts_client.get_caller_identity()
    return response['Account']

def search_ec2_instances(instance_name, aws_profile):
    """
    Search for EC2 instances matching the optional given name
    otherwise, print out all instances
    """
    session = boto3.Session(profile_name=aws_profile)
    client = session.client('config')
    expression = """
        SELECT resourceId, resourceName, resourceType, configuration.instanceType,
               availabilityZone, configuration.state.name, configuration.ipV4Addresses
        WHERE resourceType = 'AWS::EC2::Instance'
          AND configuration.state.name = 'running'
    """
    if instance_name:
        expression += f" AND resourceName = '{instance_name}'"

    account_id = get_account_id(aws_profile)

    if account_id == "123456789012": # myorg-master account ID
        configuration_aggregator_name = 'aws-controltower-ConfigAggregatorForOrganizations'
    elif account_id == "123456789012": # myorg-audit account ID
        configuration_aggregator_name = 'aws-controltower-GuardrailsComplianceAggregator'
    else:
        # Set a default Configuration Aggregator name if needed
        configuration_aggregator_name = 'default'

    response = client.select_aggregate_resource_config(
        Expression=expression,
        ConfigurationAggregatorName=configuration_aggregator_name,
        Limit=100  # this is the literal limit here, unfortunately...
    )

    config_items = response['Results']
    if config_items:
        return config_items

    return []

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--profile', required=True,
                    help='AWS profile to use for authentication')
parser.add_argument('-i', '--instance-name', required=False,
                    help='Name of the EC2 instance to search for')
args = parser.parse_args()

matching_instances = search_ec2_instances(args.instance_name, args.profile)
if matching_instances:
    for item in matching_instances:
        if isinstance(item, str):
            print(item)
            continue

        instance_id = item['ResourceId']
        instance_type = item['Configuration']['instanceType']
        state = item['Configuration']['state']['name']

        output = [
            f"Instance ID: {instance_id}",
            f"Instance Type: {instance_type}",
            f"State: {state}",
            ""  # Empty line
        ]

        print("\n".join(output))

else:
    print("No matching instances found.")

print()
