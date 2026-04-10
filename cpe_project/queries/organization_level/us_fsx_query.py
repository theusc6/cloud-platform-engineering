"""
This module is used to perform operations on AWS services using the boto3 library.
It interacts with AWS FSx across organizational accounts, retrieves data, and 
stores it in a pandas DataFrame, which is then exported to an Excel file.

The script executes the following tasks:
1. Retrieves the list of accounts in the AWS organization.
2. Excludes certain accounts based on their IDs.
3. Assumes a role in each account to gain the permissions necessary to list all FSx file systems.
4. Searches all specified AWS regions for FSx file systems in each account.
5. Retrieves and prints relevant details about each FSx file system, such as its ID, Name, 
   State, File System Type, Storage Capacity, Region, and the Account it belongs to.
6. Stores the retrieved data in a pandas DataFrame.
7. Generates a summary of FSx details.
8. Writes the DataFrame and the summary to separate sheets in an Excel file.

Functions:
    get_fsx_name: Retrieves the name of an FSx file system from its tags.
    get_fsx_backup_info: Retrieves backup information for an FSx file system.
    find_fsx_filesystems: Finds and prints FSx file systems in a given region and account.
    get_organization_accounts: Retrieves a list of accounts in the organization.
    assume_role_in_account: Assumes a role in a specified account to gain permissions.
"""
import argparse
import datetime
import boto3
import pandas as pd
from botocore.exceptions import BotoCoreError, ClientError

def get_fsx_name(fsx):
    """
    Retrieves the name of an FSx file system from its tags.

    Parameters:
    fsx (dict): An FSx file system dictionary from describe_file_systems response.

    Returns:
    str: The value of the 'Name' tag if it exists, 'N/A' otherwise.
    """
    if 'Tags' in fsx and fsx['Tags']:
        for tag in fsx['Tags']:
            if tag['Key'] == 'Name':
                return tag['Value']
    return 'N/A'

def get_fsx_backup_info(fsx_client, file_system_id):
    """
    Retrieves backup information for an FSx file system.

    Parameters:
    fsx_client (boto3.client): FSx client object.
    file_system_id (str): FSx file system ID.

    Returns:
    tuple: (backup_count, automatic_backup_retention_days)
    """
    try:
        backups_response = fsx_client.describe_backups(
            Filters=[{'Name': 'file-system-id', 'Values': [file_system_id]}]
        )
        backup_count = len(backups_response['Backups'])

        # Get automatic backup retention from file system config
        automatic_backup_retention = 'N/A'

        return backup_count, automatic_backup_retention
    except ClientError as e:
        print(f"Error retrieving backups for FSx {file_system_id}: {str(e)}")
        return 0, 'N/A'

def extract_storage_info(fsx):
    """Return storage capacity and type from FSx info."""
    return (
        fsx.get('StorageCapacity', 0),
        fsx.get('StorageType', 'N/A')
    )


def extract_network_info(fsx):
    """Return VPC and subnet info from FSx."""
    return (
        fsx.get('VpcId', 'N/A'),
        ', '.join(fsx.get('SubnetIds', []))
    )


def determine_throughput(fsx):
    """Determine throughput capacity for FSx based on type."""
    for key in ('WindowsConfiguration', 'LustreConfiguration',
                'OntapConfiguration', 'OpenZFSConfiguration'):
        cfg = fsx.get(key)
        if cfg:
            return cfg.get('ThroughputCapacity',
                           cfg.get('PerUnitStorageThroughput', 'N/A'))
    return 'N/A'


def determine_deployment(fsx):
    """Determine deployment type."""
    for key in ('WindowsConfiguration', 'LustreConfiguration',
                'OntapConfiguration', 'OpenZFSConfiguration'):
        cfg = fsx.get(key)
        if cfg:
            return cfg.get('DeploymentType', 'N/A')
    return 'N/A'


def determine_backup_retention(fsx):
    """Determine automatic backup retention days."""
    for key in ('WindowsConfiguration', 'LustreConfiguration',
                'OntapConfiguration', 'OpenZFSConfiguration'):
        cfg = fsx.get(key)
        if cfg:
            return cfg.get('AutomaticBackupRetentionDays', 'N/A')
    return 'N/A'


def assemble_fsx_record(fsx, region, acct_id, acct_name, fsx_client):
    """Build final dict for one FSx filesystem."""
    fsx_name = get_fsx_name(fsx)
    fsx_id = fsx['FileSystemId']

    storage_capacity, storage_type = extract_storage_info(fsx)
    vpc_id, subnet_ids = extract_network_info(fsx)

    backup_count, _ = get_fsx_backup_info(fsx_client, fsx_id)

    # ✅ Fix timezone error for Excel export
    creation_time = fsx.get('CreationTime')
    if isinstance(creation_time, datetime.datetime) and creation_time.tzinfo:
        creation_time = creation_time.replace(tzinfo=None)

    return {
        'File System ID': fsx_id,
        'Name': fsx_name,
        'File System Type': fsx['FileSystemType'],
        'Lifecycle State': fsx['Lifecycle'],
        'Creation Time': creation_time,
        'Storage Capacity (GB)': storage_capacity,
        'Storage Type': storage_type,
        'Throughput Capacity': determine_throughput(fsx),
        'Deployment Type': determine_deployment(fsx),
        'VPC ID': vpc_id,
        'Subnet IDs': subnet_ids,
        'DNS Name': fsx.get('DNSName', 'N/A'),
        'Owner ID': fsx.get('OwnerId', acct_id),
        'Backup Count': backup_count,
        'Auto Backup Retention (Days)': determine_backup_retention(fsx),
        'Region': region,
        'Account ID': acct_id,
        'Account Name': acct_name
    }

def find_fsx_filesystems(aws_region, session, acct_id, acct_name):
    """
    Retrieves FSx file systems in a specific region for a given account.
    """
    results = []
    try:
        fsx_client = session.client('fsx', region_name=aws_region)
        paginator = fsx_client.get_paginator('describe_file_systems')

        for page in paginator.paginate():
            for fsx in page['FileSystems']:
                record = assemble_fsx_record(fsx, aws_region, acct_id, acct_name, fsx_client)
                results.append(record)

                print(
                    f'Found FSx - ID: {record["File System ID"]}, '
                    f'Name: {record["Name"]}, '
                    f'Type: {record["File System Type"]}, '
                    f'State: {record["Lifecycle State"]}, '
                    f'Capacity: {record["Storage Capacity (GB)"]}GB, '
                    f'Deployment: {record["Deployment Type"]}, '
                    f'Region: {aws_region}, '
                    f'Account: {acct_id}'
                )

    except ClientError as err:
        code = err.response['Error']['Code']
        msg = str(err)
        print(f"Error in region {aws_region} ({acct_id}): {code} — {msg}")

    return results

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
            RoleSessionName='FSxReportGenerator'
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
        description="Script to generate AWS FSx report."
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
        "--profile_name", "-p",
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

    # Iterate through the accounts, assume role, and find FSx file systems
    output_data = []
    for acct in accounts:
        try:
            if acct['Id'] == MASTER_ACCOUNT_ID:
                account_session = master_session
            else:
                account_session = assume_role_in_account(acct['Id'],
                                                       CROSS_ACCOUNT_ROLE_NAME, master_session)

            if account_session is None:
                print(f"Skipping account {acct['Id']} due to error in assuming role.")
                continue

            print(f'Searching FSx file systems in account {acct["Id"]} ({acct["Name"]}):')

            for reg2 in regions:
                try:
                    output_data.extend(
                        find_fsx_filesystems(
                            reg2,
                            account_session,
                            acct['Id'],
                            acct['Name']
                        )
                    )
                except BotoCoreError as e:
                    print(f'Error searching region {reg2} in account {acct["Id"]}: {str(e)}')

        except BotoCoreError as e:
            print(f'Error searching account {acct["Id"]}: {str(e)}')

    # Create a DataFrame and save it to an Excel file
    df = pd.DataFrame(output_data)

    # Create summary table
    if len(df) > 0:
        summary_data = {
            'Total FSx File Systems': [len(df)],
            'Windows File Systems': [len(df[df['File System Type'] == 'WINDOWS'])],
            'Lustre File Systems': [len(df[df['File System Type'] == 'LUSTRE'])],
            'NetApp ONTAP File Systems': [len(df[df['File System Type'] == 'ONTAP'])],
            'OpenZFS File Systems': [len(df[df['File System Type'] == 'OPENZFS'])],
            'Available File Systems': [len(df[df['Lifecycle State'] == 'AVAILABLE'])],
            'Creating File Systems': [len(df[df['Lifecycle State'] == 'CREATING'])],
            'Failed File Systems': [len(df[df['Lifecycle State'] == 'FAILED'])],
            'Total Storage Capacity (GB)': [df['Storage Capacity (GB)'].sum()],
            'Average Storage Capacity (GB)': [df['Storage Capacity (GB)'].mean()],
            'File Systems with Backups': [len(df[df['Backup Count'] > 0])],
            'Total Backups': [df['Backup Count'].sum()]
        }

        # Add per-region details
        for reg in regions:
            region_data = df[df['Region'] == reg]
            summary_data[f'{reg} File Systems'] = [
                len(region_data)]
            summary_data[f'{reg} Windows FS'] = [
                len(region_data[region_data['File System Type'] == 'WINDOWS'])]
            summary_data[f'{reg} Lustre FS'] = [
                len(region_data[region_data['File System Type'] == 'LUSTRE'])]
            summary_data[f'{reg} ONTAP FS'] = [
                len(region_data[region_data['File System Type'] == 'ONTAP'])]
            summary_data[f'{reg} OpenZFS FS'] = [
                len(region_data[region_data['File System Type'] == 'OPENZFS'])]
            summary_data[f'{reg} Storage (GB)'] = [
                region_data['Storage Capacity (GB)'].sum()]

        # Add per-account summary
        account_summary = df.groupby('Account Name').agg({
            'File System ID': 'count',
            'Storage Capacity (GB)': 'sum',
            'Backup Count': 'sum'
        }).to_dict()

        for account_name in df['Account Name'].unique():
            summary_data[f'{account_name} File Systems'] = [
                account_summary['File System ID'][account_name]]
            summary_data[f'{account_name} Storage (GB)'] = [
                account_summary['Storage Capacity (GB)'][account_name]]
            summary_data[f'{account_name} Backups'] = [
                account_summary['Backup Count'][account_name]]
    else:
        summary_data = {
            'Total FSx File Systems': [0],
            'Message': ['No FSx file systems found in any account/region']
        }

    # Convert to DataFrame for Excel output
    summary_table = pd.DataFrame(summary_data)

    # Save main table and summary table to the same Excel file
    with pd.ExcelWriter('AWS_FSx_Report-AllRegions.xlsx') as writer:
        df.to_excel(writer, sheet_name='FSx Details', index=False)
        summary_table.T.to_excel(writer, sheet_name='Summary', index=True, header=['Count'])

    print("Report generated successfully!")
    print(f"Total FSx file systems found: {len(df)}")
    print("Report saved to: AWS_FSx_Report-AllRegions.xlsx")
