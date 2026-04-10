"""
This module contains functions and classes for working with dates, times, 
and timezones using the datetime and zoneinfo libraries. 

It provides functionality for converting between different timezones, 
creating datetime objects, and more.
"""
from datetime import datetime
import argparse
from zoneinfo import ZoneInfo
from botocore.exceptions import BotoCoreError, ClientError
import boto3
import pandas as pd

VALIDATION_METHOD = "Validation Method"

# Add the regions list
regions = [
    "us-west-1", 
    "us-west-2", 
    "us-east-1", 
    "us-east-2", 
    "ap-southeast-1", 
    "me-south-1", 
    "me-central-1", 
    "ap-east-1"
]

def get_certificate_details(acm, certificate_summary, account_id, account_name, aws_region):
    """
    Retrieves detailed information about an ACM certificate.

    This function calls the AWS Certificate Manager (ACM) to describe an individual certificate
    and compiles its details into a dictionary that includes the domain name, certificate ARN,
    account ID, account name, status, region, validation method, and days to expiry.

    Parameters:
    acm (boto3.client): The ACM client instance used to interact with AWS ACM.
    certificate_summary (dict): A dictionary containing a summary of the ACM certificate.
    account_id (str): The AWS account ID where the certificate resides.
    account_name (str): The name associated with the AWS account ID.
    aws_region (str): The AWS region where the certificate is deployed.

    Returns:
    dict: A dictionary containing detailed information about the ACM certificate.
    """
    certificate_arn = certificate_summary['CertificateArn']
    certificate_detail = acm.describe_certificate(CertificateArn=certificate_arn)['Certificate']

    # Create dictionary with certificate details
    cert_dict = {
        'Domain Name': certificate_detail.get('DomainName', 'N/A'),
        'Certificate ARN': certificate_arn,
        'Account ID': account_id,
        'Account Name': account_name,
        'Status': certificate_detail.get('Status', 'N/A'),
        'Region': aws_region,
        VALIDATION_METHOD: get_validation_method(certificate_detail),
        'Days to Expiry': calculate_days_to_expiry(certificate_detail)
    }

    return cert_dict

def print_certificate(cert_dict):
    """
    Prints the details of an ACM certificate.

    This function formats and outputs the certificate details to the console.

    Parameters:
    cert_dict (dict): A dictionary containing the certificate details such as domain name,
                      status, days to expiry, validation method, account ID, and region.

    Returns:
    None
    """
    print((
        f'Found ACM Certificate - Domain Name: {cert_dict["Domain Name"]}, '
        f'Status: {cert_dict["Status"]}, '
        f'Days to Expiry: {cert_dict["Days to Expiry"]}, '
        f'Validation Method: {cert_dict[VALIDATION_METHOD]}, '
        f'Account: {cert_dict["Account ID"]}, '
        f'Region: {cert_dict["Region"]}'
    ))

def find_acm_certificates(session, account_id, account_name, aws_region):
    """
    Searches for ACM (AWS Certificate Manager) certificates in a specified AWS region 
    and account.

    Parameters:
    session (boto3.Session): The boto3 Session object for the current account.
    account_id (str): The ID of the AWS account.
    account_name (str): The name of the AWS account.
    region (str): The AWS region to search in.

    Returns:
    data (list): A list of dictionaries, where each dictionary contains details 
    about an ACM certificate.
    """
    acm = session.client('acm', region_name=aws_region)
    paginator = acm.get_paginator('list_certificates')
    data = []

    for page in paginator.paginate():
        for certificate_summary in page['CertificateSummaryList']:
            cert_dict = get_certificate_details(
                acm, certificate_summary, account_id, account_name, aws_region
            )
            data.append(cert_dict)
            print_certificate(cert_dict)

    return data

def get_validation_method(certificate_detail):
    """
    Retrieves the validation method from a certificate detail object.

    Parameters:
    certificate_detail (dict): A dictionary containing details of the certificate.

    Returns:
    str: The validation method if present, otherwise 'Unknown'.
    """
    if 'DomainValidationOptions' in certificate_detail:
        for option in certificate_detail['DomainValidationOptions']:
            if 'ValidationMethod' in option:
                return option['ValidationMethod']
    return 'Unknown'

def calculate_days_to_expiry(certificate_detail):
    """
    Calculates the number of days until the certificate expires.

    Parameters:
    certificate_detail (dict): A dictionary containing details of the certificate.

    Returns:
    int or str: The number of days to expiry if the 'NotAfter' key is present,
                otherwise 'N/A'.
    """
    if 'NotAfter' in certificate_detail:
        expiry_time = certificate_detail['NotAfter'] - datetime.now(tz=ZoneInfo("UTC"))
        return expiry_time.days
    return 'N/A'

def get_organization_accounts(master_sess):
    """
    Fetches a list of accounts from an AWS organization.
    
    Parameters:
    master_session (boto3.Session): The boto3 Session object for the master account.
    
    Returns:
    accounts (list): A list of account dictionaries with "Id" and "Name" keys.
    """
    organizations = master_sess.client('organizations')
    paginator = organizations.get_paginator('list_accounts')
    accounts_list = []

    for page in paginator.paginate():
        accounts_list.extend(page['Accounts'])

    for account in accounts_list:
        print(f'Account ID: {account["Id"]}, Name: {account["Name"]}')

    return accounts_list


def col_num_to_letter(col_num):
    """
    Converts a column number into Excel column letter.
    
    Parameters:
    col_num (int): Column number to convert.

    Returns:
    string (str): Excel column letter (e.g., 'A' for 1, 'Z' for 26, 'AA' for 27, etc.)
    """
    string = ""
    while col_num > 0:
        col_num, remainder = divmod(col_num - 1, 26)
        string = chr(65 + remainder) + string
    return string

# Function to assume a role in a specified account


def assume_role_in_account(account_id, role_name, session):
    """
    Assumes a specified IAM role in the provided AWS account.
    
    Parameters:
    account_id (str): The ID of the AWS account.
    role_name (str): The name of the IAM role to assume.
    master_session (boto3.Session): The boto3 Session object for the master account.

    Returns:
    response (dict): The response from the assume_role operation.
    """
    print(
        f'\nAssuming role in account {account_id}: arn:aws:iam::{account_id}:role/{role_name}')
    sts = session.client('sts')
    response = sts.assume_role(
        RoleArn=f'arn:aws:iam::{account_id}:role/{role_name}',
        RoleSessionName='IAMUserFinder'
    )

    return boto3.Session(
        aws_access_key_id=response['Credentials']['AccessKeyId'],
        aws_secret_access_key=response['Credentials']['SecretAccessKey'],
        aws_session_token=response['Credentials']['SessionToken']
    )


def parse_arguments():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Script to generate AWS ACM certificate report."
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
        '-p',
        "--profile_name",
        required=True,
        default="n/a",
        help="AWS profile name. Default: default"
    )

    return parser.parse_args()

CROSS_ACCOUNT_ROLE_NAME = 'OrganizationAccountAccessRole'

if __name__ == '__main__':
    args = parse_arguments()

    master_session = boto3.Session(profile_name=args.profile_name)
    accounts = get_organization_accounts(master_session)
    print(f'Found {len(accounts)} accounts in the organization.')

    # Add master account to the list of accounts
    MASTER_ACCOUNT_ID = args.master_account_id
    MASTER_ACCOUNT_NAME = args.master_account_name
    master_account = {'Id': MASTER_ACCOUNT_ID, 'Name': MASTER_ACCOUNT_NAME}

    # Remove the master account from the list
    accounts = [account for account in accounts if account['Id']
                != MASTER_ACCOUNT_ID]
    accounts.append(master_account)

    # Add excluded account IDs if needed. Suspended accounts may create unnecessary errors,
    # thus they may be added here
    excluded_account_ids = ['123456789012',
                            '123456789012', 
                            '123456789012', 
                            '123456789012', 
                            '123456789012', 
                            '123456789012', 
                            '123456789012',
                            '123456789012', 
                            '123456789012', 
                            '123456789012']

    # Exclude the specified accounts from the list
    accounts = [account for account in accounts if account['Id']
                not in excluded_account_ids]

    # Iterate through the accounts, assume role, and find ACM certificates
    output_data = []
    for acct in accounts:
        try:
            if acct['Id'] == MASTER_ACCOUNT_ID:
                account_session = master_session
            else:
                account_session = assume_role_in_account(
                    acct['Id'], CROSS_ACCOUNT_ROLE_NAME, master_session)

            for region in regions:
                message = (
                    f'Searching ACM certificates in account {acct["Id"]} '
                    f'({acct["Name"]}) in region {region}:'
                )
                print(message)
                output_data.extend(
                    find_acm_certificates(
                        account_session,
                        acct['Id'],
                        acct['Name'],
                        region
                    )
                )
        except (BotoCoreError, ClientError) as e:
            print(f'Error searching account {acct["Id"]}: {str(e)}')

    # Create a DataFrame and save it to an Excel file
    df = pd.DataFrame(output_data)

    # Create summary table
    summary_data = {
        'Total ACM Certificates': [len(df)]
    }

    for acct in accounts:
        # Filtering dataframe
        filtered_df = df[df['Account ID'] == acct['Id']]

        # Assigning the length to the dictionary
        account_key = f'{acct["Name"]} ({acct["Id"]})'
        summary_data[account_key] = [len(filtered_df)]

    # Add certificate count by validation method
    for unique_method in df[VALIDATION_METHOD].unique():
        # Filtering dataframe
        filtered_df = df[df[VALIDATION_METHOD] == unique_method]

        # Counting the length and assigning to the dictionary
        summary_data[f'Total {unique_method} Certificates'] = [
            len(filtered_df)]

    summary_table = pd.DataFrame(summary_data)

    # Save main table and summary table to the same Excel file
    with pd.ExcelWriter('US_ACM_Certificate_Report-AllRegions.xlsx', engine='xlsxwriter') as writer:  # pylint: disable=abstract-class-instantiated
        df.to_excel(writer, sheet_name='ACM Certificate Details', index=False)
        summary_table.T.to_excel(
            writer, sheet_name='Summary', index=True, header=False)

        # Apply conditional formatting to highlight cells with <= 30 days to expiry
        workbook = writer.book
        worksheet = writer.sheets['ACM Certificate Details']
        red_format = workbook.add_format(
            {'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
        days_to_expiry_col_letter = col_num_to_letter(
            df.columns.get_loc('Days to Expiry') + 1)
        format_dict = {'type': 'cell', 'criteria': '<=',
                    'value': 30, 'format': red_format}
        range_str = f'{days_to_expiry_col_letter}2:{days_to_expiry_col_letter}{len(df) + 1}'

        worksheet.conditional_format(range_str, format_dict)
