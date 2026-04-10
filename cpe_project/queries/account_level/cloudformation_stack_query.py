"""
This script fetches details of AWS CloudFormation stacks and their associated resources
across multiple AWS regions and exports the data to an Excel file using pandas.

The script allows the user to specify the AWS CLI profile and regions to query for
CloudFormation stack information. For each CloudFormation stack, it captures details 
like Stack Name, Stack ID, Stack Status, Creation Time, Last Updated Time, Region, 
Tags, Capabilities, and associated resources such as Resource Type, Logical Resource ID,
Physical Resource ID, and Resource Status.

Usage:
    python3 cloudformation_stack_query.py --profile <profile_name> --regions <region1> <region2> ...

Example:
    python3 cloudformation_stack_query.py --profile default --regions us-east-1 us-west-2

Required Arguments:
    --profile: AWS CLI profile name for authentication.
    --regions: Space-separated list of AWS regions to fetch CloudFormation stacks from.

Output:
    The script generates an Excel file named
    'cloudformation_stacks_and_resources_<account_id>_<date>.xlsx'
    containing details of the CloudFormation stacks and their associated resources.
"""
from datetime import datetime
import argparse
import boto3
import pandas as pd


def get_cloudformation_stacks_with_resources(cfn_client, region):
    """
    Fetches all CloudFormation stacks and their associated resources for a given region.
    """
    stacks = cfn_client.describe_stacks()['Stacks']
    stacks_list = []

    for stack in stacks:
        stack_resources = cfn_client.describe_stack_resources(
            StackName=stack['StackName'])['StackResources']

        # Handle timezones for stack creation and last update
        creation_time = (
            stack.get('CreationTime', 'N/A').replace(tzinfo=None)
            if stack.get('CreationTime') else 'N/A'
        )
        last_updated_time = (
            stack.get('LastUpdatedTime', 'N/A').replace(tzinfo=None)
            if stack.get('LastUpdatedTime') else 'N/A'
        )

        stacks_list.append({
            'StackName': stack['StackName'],
            'StackId': stack['StackId'],
            'StackStatus': stack['StackStatus'],
            'CreationTime': creation_time,
            'LastUpdatedTime': last_updated_time,
            'Region': region,
            'Tags': stack.get('Tags', []),
            'Capabilities': stack.get('Capabilities', []),
            'Resources': stack_resources
        })

        print(f"Gathering information for stack {stack['StackName']}..")

    return stacks_list


def expand_stack_data_with_resources(stacks_list):
    """
    Expands stack data by duplicating stack-level information for each resource in the stack.

    :param stacks_list: A list of dictionaries with CloudFormation stack and resource details.
    :return: A dictionary with stack names as keys and their detailed data as values.
    """
    expanded_data = {}

    for stack in stacks_list:
        stack_name = stack['StackName']
        tag_keys = ', '.join(tag['Key'] for tag in stack['Tags']) if stack['Tags'] else 'N/A'
        tag_values = ', '.join(tag['Value'] for tag in stack['Tags']) if stack['Tags'] else 'N/A'
        capabilities = ', '.join(stack['Capabilities'])

        # Prepare data for each stack to be added to its own DataFrame
        stack_data = []

        for resource in stack['Resources']:
            stack_data.append({
                'StackName': stack_name,
                'StackId': stack['StackId'],
                'StackStatus': stack['StackStatus'],
                'CreationTime': stack['CreationTime'],
                'LastUpdatedTime': stack['LastUpdatedTime'],
                'Region': stack['Region'],
                'TagKeys': tag_keys,
                'TagValues': tag_values,
                'Capabilities': capabilities,
                'ResourceType': resource['ResourceType'],
                'LogicalResourceId': resource['LogicalResourceId'],
                'PhysicalResourceId': resource.get('PhysicalResourceId', 'N/A'),
                'ResourceStatus': resource['ResourceStatus']
            })

        # Store the data for the stack
        expanded_data[stack_name] = pd.DataFrame(stack_data)

    return expanded_data


def export_stacks_to_excel_with_resources(stacks_data, file_name):
    """
    Exports CloudFormation stack and resource details to an Excel file
    with each stack on a separate sheet.

    :param stacks_data: A dictionary with stack names as keys and DataFrames as values.
    :param file_name: Name of the Excel file to create.
    """
    with pd.ExcelWriter(file_name) as writer:
        for stack_name, data_frame in stacks_data.items():
            # Write each DataFrame to a separate sheet named after the stack
            data_frame.to_excel(writer, sheet_name=stack_name[:31], index=False)
            # Note: Excel sheet names have a max length of 31 characters.

    print(f'Successfully created {file_name} with each CloudFormation stack on a separate sheet.')


def main():
    """
    Main function to process command-line arguments and initiate stack
    and resource fetching and exporting.
    """
    # Initialize the argument parser
    parser = argparse.ArgumentParser(description='List CloudFormation '
                                     'stacks and resources to an Excel file.')
    parser.add_argument('-p', '--profile', type=str, required=True, help='AWS CLI profile name')
    parser.add_argument('-r', '--regions', type=str, required=True, nargs='+',
                        help='AWS regions (space-separated)')

    # Parse arguments
    args = parser.parse_args()

    # Configure Boto3 to use the specified profile
    boto3.setup_default_session(profile_name=args.profile)

    # Get the account_id from the current session
    account_id = boto3.client('sts').get_caller_identity().get('Account')

    date_time = datetime.now().date()
    file_name = f'cloudformation_stacks_and_resources_{account_id}_{date_time}.xlsx'

    # Initialize an empty list to collect stacks and resources from all regions
    all_stacks = []

    # Loop through the regions provided and fetch stacks for each region
    for region in args.regions:
        print(f"Fetching stacks from region: {region}")
        cfn_client = boto3.client('cloudformation', region_name=region)
        region_stacks = get_cloudformation_stacks_with_resources(cfn_client, region)
        all_stacks.extend(region_stacks)

    # Expand stack data and prepare DataFrames for each stack
    stacks_data = expand_stack_data_with_resources(all_stacks)

    # Export all stack data to the Excel file with each stack in a separate sheet
    export_stacks_to_excel_with_resources(stacks_data, file_name)


if __name__ == "__main__":
    main()
