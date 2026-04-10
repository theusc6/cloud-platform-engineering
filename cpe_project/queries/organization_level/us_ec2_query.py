"""
This module is used to perform operations on AWS services using the boto3 library.
It interacts with AWS EC2 instances and organizational accounts, retrieves data, and 
stores it in a pandas DataFrame, which is then exported to an Excel file.

The script executes the following tasks:
1. Retrieves the list of accounts in the AWS organization.
2. Excludes certain accounts based on their IDs.
3. Assumes a role in each account to gain the permissions necessary to list all EC2 instances.
4. Searches all specified AWS regions for EC2 instances in each account.
5. Retrieves and prints relevant details about each instance, such as its ID, Name, 
State, Platform, Region, and the Account it belongs to.
6. Stores the retrieved data in a pandas DataFrame.
7. Generates a summary of instance details.
8. Writes the DataFrame and the summary to separate sheets in an Excel file.

Functions:
    get_instance_name: Retrieves the name of an EC2 instance from its tags.
    find_ec2_instances: Finds and prints EC2 instances in a given region and account.
    get_organization_accounts: Retrieves a list of accounts in the organization.
    assume_role_in_account: Assumes a role in a specified account to gain permissions.
"""
import argparse
import boto3
import pandas as pd
from botocore.exceptions import BotoCoreError, ClientError

def get_instance_name(instance):
    """
    Retrieves the name of an EC2 instance from its tags.

    Parameters:
    instance (boto3.EC2.Instance): An EC2 Instance resource.

    Returns:
    str: The value of the 'Name' tag if it exists, 'N/A' otherwise.
    """
    if instance.tags:
        for tag in instance.tags:
            if tag['Key'] == 'Name':
                return tag['Value']
    return 'N/A'

def find_ec2_instances(aws_region, session, account_id, account_name):
    """
    Retrieves and prints the details of all EC2 instances within a 
    specific region for a given account.

    Parameters:
    region (str): The name of the region where instances are located.
    session (boto3.Session): A valid boto3 Session object.
    account_id (str): The AWS account ID where instances are located.
    account_name (str): The name associated with the AWS account.

    Returns:
    list: A list of dictionaries, where each dictionary contains details of an EC2 instance.
    """
    try:
        ec2 = session.resource('ec2', region_name=aws_region)
        instances = ec2.instances.all()

        data = []
        for instance in instances:
            platform = instance.platform if instance.platform else 'linux'
            instance_state = instance.state["Name"]
            if instance_state in ('stopped', 'running'):
                instance_name = get_instance_name(instance)

                # Get all tags as a dictionary
                tags_dict = {}
                if instance.tags:
                    tags_dict = {tag['Key']: tag.get('Value', '') for tag in instance.tags}

                # Get availability zone
                availability_zone = instance.placement.get('AvailabilityZone', 'N/A') if instance.placement else 'N/A'

                # Get public IP (may be None)
                public_ip = instance.public_ip_address if instance.public_ip_address else 'N/A'

                data.append({
                    'Instance ID': instance.id,
                    'Name': instance_name, 
                    'State': instance_state, 
                    'Platform': platform,
                    'Instance Type': instance.instance_type,
                    'Availability Zone': availability_zone,
                    'Region': aws_region, 
                    'Account ID': account_id, 
                    'Account Name': account_name,
                    'Private IP': instance.private_ip_address if instance.private_ip_address else 'N/A',
                    'Public IP': public_ip,
                    'Tags': str(tags_dict)  # Convert dict to string for Excel compatibility
                })

                print(f'Found EC2 Instance - ID: {instance.id}, '
                    f'Name: {instance_name}, '
                    f'State: {instance_state}, '
                    f'Platform: {platform}, '
                    f'Instance Type: {instance.instance_type}, '
                    f'AZ: {availability_zone}, '
                    f'Region: {aws_region}, '
                    f'Account: {account_id}, '
                    f'Private IP: {instance.private_ip_address if instance.private_ip_address else "N/A"}, '
                    f'Public IP: {public_ip}')
        return data
    except ClientError as client_error:
        if client_error.response['Error']['Code'] == 'UnauthorizedOperation':
            print(f"Unexpected error: {str(client_error)}")
        return []  # return empty list if unauthorized


def get_organization_accounts(master_sess):
    """
    Fetches a list of accounts in the organization using the provided session.

    Args:
        master_sess (boto3.Session): A session object which 
        represents a configuration state for operations.

    Returns:
        accounts (list): A list of dictionaries, each containing 
        the ID and Name of an account in the organization.
    """
    organizations = master_sess.client('organizations')
    paginator = organizations.get_paginator('list_accounts')
    accounts_list = []

    for page in paginator.paginate():
        accounts_list.extend(page['Accounts'])

    for account in accounts_list:
        print(f'Account ID: {account["Id"]}, Name: {account["Name"]}')

    return accounts_list

def assume_role_in_account(account_id, role_name, session):
    """
    Assumes a role in the given account and creates a new 
    session with the assumed role's credentials.

    Args:
        account_id (str): The ID of the AWS account where the role is to be assumed.
        role_name (str): The name of the role to be assumed.
        session (boto3.Session): The existing boto3 session from which STS client is created.

    Returns:
        boto3.Session: A new boto3 Session object with the assumed role's credentials.
    """
    try:
        print(f'\nAssuming role in account '
            f'{account_id}: arn:aws:iam::{account_id}:role/{role_name}') 
        sts = session.client('sts')
        response = sts.assume_role(
            RoleArn=f'arn:aws:iam::{account_id}:role/{role_name}',
            RoleSessionName='WindowsEC2InstanceFinder'
        )

        return boto3.Session(
            aws_access_key_id=response['Credentials']['AccessKeyId'],
            aws_secret_access_key=response['Credentials']['SecretAccessKey'],
            aws_session_token=response['Credentials']['SessionToken']
        )
    except ClientError as client_error:
        print(f"Failed to assume role in account {account_id}. Error: {str(client_error)}")
        return None

def parse_arguments():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Script to generate AWS Ec2 report."
    )

    parser.add_argument(
        "--master_account_id",
        default="123456789012",
        help="AWS Master account id. Default: 123456789012"
    )

    parser.add_argument(
        "--master_account_name",
        default="myorg-master",
        help="AWS Master account name. Default: myorg-master"
    )

    parser.add_argument(
        "--profile_name",
        required=True,
        default="n/a",
        help="AWS profile name. Default: default"
    )

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()

    PROFILE_NAME = args.profile_name
    master_session = boto3.Session(profile_name=args.profile_name)
    regions = [
            "us-west-2",
            "us-east-1",
            "us-east-2",
            "eu-west-2",
            "ap-southeast-1",
            "ap-east-1",
            "us-west-1"
        ]
    accounts = get_organization_accounts(master_session)
    print(f'Found {len(accounts)} accounts in the organization.')
    CROSS_ACCOUNT_ROLE_NAME = 'OrganizationAccountAccessRole'

    # Add master account to the list of accounts
    MASTER_ACCOUNT_ID = args.master_account_id
    MASTER_ACCOUNT_NAME = args.master_account_name
    master_account = {'Id': MASTER_ACCOUNT_ID, 'Name': MASTER_ACCOUNT_NAME}

    # Add excluded account IDs - these are excluded due to 'suspended' status.
    # Accounts will be deleted in 90 days from suspension date
    excluded_account_ids = []

    # Remove the master account and excluded accounts from the list
    accounts = [account for account in accounts if account['Id'] != MASTER_ACCOUNT_ID
                and account['Id'] not in excluded_account_ids]
    accounts.append(master_account)

    # Iterate through the accounts, assume role, and find EC2 instances
    output_data = []
    for acct in accounts:
        try:
            if acct['Id'] == MASTER_ACCOUNT_ID:
                account_session = master_session
            else:
                account_session = assume_role_in_account(acct['Id'],
                CROSS_ACCOUNT_ROLE_NAME, master_session)

            print(f'Searching Windows EC2 instances in account  '
                f'{acct["Id"]} ({acct["Name"]}):'
                )

            if account_session is None:
                print(f"Skipping account {acct['Id']} due to error in assuming role.")
                continue

            print(f'Searching Windows EC2 instances in account  '
                f'{acct["Id"]} ({acct["Name"]}):' )

            for region in regions:
                try:
                    output_data.extend(
                        find_ec2_instances(
                            region,
                            account_session,
                            acct['Id'],
                            acct['Name']
                        )
                    )
                except BotoCoreError as e:
                    print(f'Error searching region {region} in account {acct["Id"]}: {str(e)}')

        except BotoCoreError as e:
            print(f'Error searching account {acct["Id"]}: {str(e)}')

    # Create a DataFrame and save it to an Excel file
    df = pd.DataFrame(output_data)

    # Check if DataFrame is empty and create summary accordingly
    if df.empty:
        print("\nNo EC2 instances found. Creating empty report with zero counts.")
        summary_data = {
            'Total Linux Instances': [0],
            'Running Linux Instances': [0],
            'Stopped Linux Instances': [0],
            'Total Windows Instances': [0],
            'Running Windows Instances': [0],
            'Stopped Windows Instances': [0]
        }

        # Add per-region details with zeros
        for region in regions:
            summary_data[f'{region} Instances'] = [0]
            summary_data[f'{region} Running Linux Instances'] = [0]
            summary_data[f'{region} Stopped Linux Instances'] = [0]
            summary_data[f'{region} Running Windows Instances'] = [0]
            summary_data[f'{region} Stopped Windows Instances'] = [0]

        summary_table = pd.DataFrame(summary_data)
    else:
        # Create summary table with actual data
        summary_data = {
            'Total Linux Instances': [len(df[df['Platform'] == 'linux'])],
            'Running Linux Instances': [len(df[(df['Platform'] == 'linux') & (df['State'] == 'running')])],
            'Stopped Linux Instances': [len(df[(df['Platform'] == 'linux') & (df['State'] == 'stopped')])],
            'Total Windows Instances': [len(df[df['Platform'] == 'windows'])],
            'Running Windows Instances': [len(df[(df['Platform'] == 'windows') & (df['State'] == 'running')])],
            'Stopped Windows Instances': [len(df[(df['Platform'] == 'windows') & (df['State'] == 'stopped')])]
        }

        # Add per-region details
        for region in regions:
            summary_data[f'{region} Instances'] = [len(df[df['Region'] == region])]
            summary_data[f'{region} Running Linux Instances'] = [
                len(df[(df['Region'] == region) & (df['Platform'] == 'linux') & (df['State'] == 'running')])
            ]
            summary_data[f'{region} Stopped Linux Instances'] = [
                len(df[(df['Region'] == region) & (df['Platform'] == 'linux') & (df['State'] == 'stopped')])
            ]
            summary_data[f'{region} Running Windows Instances'] = [
                len(df[(df['Region'] == region) & (df['Platform'] == 'windows') & (df['State'] == 'running')])
            ]
            summary_data[f'{region} Stopped Windows Instances'] = [
                len(df[(df['Region'] == region) & (df['Platform'] == 'windows') & (df['State'] == 'stopped')])
            ]

        # Count instances by type
        instance_type_counts = df['Instance Type'].value_counts().to_dict()

        # Add instance type counts to summary data
        for instance_type, count in instance_type_counts.items():
            summary_data[f'Instance Type: {instance_type}'] = [count]

        # Convert to DataFrame for Excel output
        summary_table = pd.DataFrame(summary_data)

    # Save main table and summary table to the same Excel file
    with pd.ExcelWriter('US_Ec2_Report-AllRegions.xlsx') as writer:  # pylint: disable=abstract-class-instantiated
        df.to_excel(writer, sheet_name='Instance Details', index=False)
        summary_table.T.to_excel(writer, sheet_name='Summary', index=True, header=True)

    print("Report generated successfully: US_Ec2_Report-AllRegions.xlsx")
    print(f"Total instances found: {len(df)}")
