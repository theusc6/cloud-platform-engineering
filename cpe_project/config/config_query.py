"""
This script runs AWS Config query for an AWS account
"""

import argparse
import json
import boto3
import yaml
from botocore.exceptions import ClientError

def run_config_query(aws_profile, query_file, aggregator=None, output=None):
    """
    This function runs the AWS Config query
    """
    # Initialize the AWS Config client
    # Setup the session using an SSO profile
    boto3.setup_default_session(profile_name=aws_profile)
    config_client = boto3.client('config')

    try:
        # Read the query from the file with explicit encoding
        with open(query_file, 'r', encoding='utf-8') as file:
            query = file.read()

        # Run the query
        if aggregator:
            response = config_client.select_aggregate_resource_config(
                Expression=query,
                ConfigurationAggregatorName=aggregator,
                Limit=100
            )
        else:
            response = config_client.select_resource_config(
                Expression=query,
                Limit=100
            )

        # Extract and print the results
        results = response['Results']
        print("Query Results:")
        for result in results:
            # Load the string into a dictionary
            data = json.loads(result)

            # Check if user wants json
            if output == 'json':
                # dump for json
                pretty_s = json.dumps(data, indent=2)
            else:
                # Convert to yaml
                pretty_s = yaml.safe_dump(data, allow_unicode=True, default_flow_style=False)

            print(pretty_s)

    except ClientError as error:
        print(f"AWS Client Error: {str(error)}")
    except FileNotFoundError as error:
        print(f"File Not Found Error: {str(error)}")

def main():
    """
    Main function to parse arguments and call run_config_query
    """
    parser = argparse.ArgumentParser(description='Run AWS Config query for an AWS account')
    parser.add_argument('aws_profile', type=str, help='AWS profile')
    parser.add_argument('query_file', type=str, help='File containing the query')
    parser.add_argument('-aggregator', type=str, help='Use the specified Aggregator')
    parser.add_argument('-output', type=str, help='[default yaml] or json')
    args = parser.parse_args()

    run_config_query(args.aws_profile, args.query_file, args.aggregator, args.output)


if __name__ == '__main__':
    main()
