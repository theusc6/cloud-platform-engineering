#!/usr/bin/env python3

"""
Count ec2 instances

"""

import argparse
import json
import boto3
from tabulate import tabulate

parser = argparse.ArgumentParser(description='Retrieve EC2 instances managed by AWS Config.')
parser.add_argument('-p', '--profile', type=str, required=True, help='AWS profile.')
args = parser.parse_args()

session = boto3.Session(profile_name=args.profile)
config = session.client('config')

# Get the list of configuration aggregators
aggregators = config.describe_configuration_aggregators()

for aggregator in aggregators['ConfigurationAggregators']:
    aggregator_name = aggregator['ConfigurationAggregatorName']

    # Query for EC2 instances
    QUERY = """
    SELECT
      resourceId,
      resourceName,
      resourceType,
      configuration.instanceType,
      accountId,
      awsRegion,
      configuration.state.name,
      resourceCreationTime
    WHERE
      resourceType = 'AWS::EC2::Instance'
    ORDER BY
      accountId
    """

    results = config.select_aggregate_resource_config(
        ConfigurationAggregatorName=aggregator_name,
        Expression=QUERY
    )

    print(f"\nAggregator: {aggregator_name}")

    if not results['Results']:
        print("No EC2 instances were found.")
        continue

    # Prepare table data
    table_data = []
    headers = ["Account ID", "Resource ID", "Instance Type", "Region", "Creation Time", "State"]

    for result_str in results['Results']:
        instance_data = json.loads(result_str)
        configuration = instance_data['configuration']
        
        table_data.append([
            instance_data['accountId'],
            instance_data['resourceId'],
            configuration['instanceType'],
            instance_data['awsRegion'],
            instance_data['resourceCreationTime'],
            configuration['state']['name']
        ])

    # Print formatted table
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    print(f"\nTotal instances: {len(table_data)}")
