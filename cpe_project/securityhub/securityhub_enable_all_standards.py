"""
This module provides a script to enable specific security standards in AWS Security Hub
for accounts in an AWS Organization. The script can target a specific account or all
accounts in the organization and can be executed for a specific AWS region.

Functions:
    get_organization_accounts(master_sess): Retrieves a list of accounts in the AWS Organization.
    enable_standards(session, standards_arns): Enables specified security
    standards in AWS Security Hub.
    parse_arguments(): Parses command-line arguments for profile name, region, and account ID.
    main(): Main function to coordinate the enabling of security standards.

Usage:
    python script_name.py --profile_name <AWS profile name> --region <AWS region>
    [--account_id <AWS account ID>]

If the account_id argument is omitted, the script will process all accounts in the organization.
"""

import argparse
import boto3
from botocore.exceptions import ClientError

def get_organization_accounts(master_sess):
    """
    Retrieves a list of accounts in the AWS Organization.

    Args:
        master_sess (boto3.Session): The Boto3 session object for the master account.

    Returns:
        list: A list of dictionaries containing account information. Each dictionary
        includes details about the account, such as its ID and name.

    This function makes use of the AWS Organizations service to fetch all the accounts
    under the specified master session. It uses pagination to ensure all accounts are
    retrieved.
    """
    organizations = master_sess.client('organizations')
    paginator = organizations.get_paginator('list_accounts')
    accounts_list = []

    for page in paginator.paginate():
        accounts_list.extend(page['Accounts'])

    return accounts_list

def assume_role_in_account(account_id, session, region_name):
    """
    Assumes a role in the given account and creates a
    new session with the assumed role's credentials.

    Args:
        account_id (str): The ID of the AWS account where the role is to be assumed.
        session (boto3.Session): The existing boto3 session from which the STS client is created.

    Returns:
        boto3.Session: A new boto3 Session object with the assumed
        role's credentials, or None if an error occurred.
    """
    role_name = 'OrganizationAccountAccessRole'  # Specify the correct role name here

    try:
        print(f'Assuming role in account {account_id}: arn:aws:iam::{account_id}:role/{role_name}')
        sts = session.client('sts')
        response = sts.assume_role(
            RoleArn=f'arn:aws:iam::{account_id}:role/{role_name}',
            RoleSessionName='AssumedSession'
        )

        return boto3.Session(
            aws_access_key_id=response['Credentials']['AccessKeyId'],
            aws_secret_access_key=response['Credentials']['SecretAccessKey'],
            aws_session_token=response['Credentials']['SessionToken'],
            region_name=region_name

        )
    except ClientError as client_error:
        print(f"Failed to assume role in account {account_id}. Error: {str(client_error)}")
        return None


def enable_standards(session, standards_arns):
    """
    Enables the specified security standards in AWS Security Hub for a given session.

    Args:
        session (boto3.Session): The Boto3 session object.
        standards_arns (list): A list of ARNs (Amazon Resource Names) representing the
            security standards to be enabled.

    Each standard specified by its ARN will be enabled, and any errors encountered
    during the process will be printed to the console.
    """
    securityhub = session.client('securityhub')
    for arn in standards_arns:
        try:
            securityhub.batch_enable_standards(
                StandardsSubscriptionRequests=[
                    {
                        'StandardsArn': arn
                    },
                ]
            )
            print(f"Enabled standard: {arn}")
        except ClientError as client_error:
            print(f"Error enabling standard {arn}: {client_error}")

def parse_arguments():
    """
    Parse command-line arguments for AWS profile name, region, and account ID.
    The profile name and region are required, while the account ID is optional.
    If no account ID is provided, all accounts in the organization will be processed.

    Returns:
        argparse.Namespace: Parsed arguments containing profile_name, region, and account_id.
    """
    parser = argparse.ArgumentParser(
        description="Enable security standards in AWS Security Hub "
        "for specific or all accounts in an organization"
    )

    parser.add_argument("-p","--profile_name", required=True, help="AWS profile name.")
    parser.add_argument("-r","--region", required=True, help="AWS region.")
    parser.add_argument("-a","--account_id", help="AWS account ID for specific "
                        "account processing. Leave blank to process all accounts.")

    return parser.parse_args()

def main():
    """
    Main function
    """
    args = parse_arguments()
    master_session = boto3.Session(profile_name=args.profile_name, region_name=args.region)

    if args.account_id:
        accounts = [{'Id': args.account_id}]
        session = master_session
    else:
        accounts = get_organization_accounts(master_session)

    standards_arns = [
        "arn:aws:securityhub:::ruleset/cis-aws-foundations-benchmark/v/1.2.0",
        f"arn:aws:securityhub:{args.region}::standards/aws-foundational-"
        f"security-best-practices/v/1.0.0",
        f"arn:aws:securityhub:{args.region}::standards/pci-dss/v/3.2.1",
        f"arn:aws:securityhub:{args.region}::standards/cis-aws-foundations-benchmark/v/1.4.0",
        f"arn:aws:securityhub:{args.region}::standards/nist-800-53/v/5.0.0",
    ]

    for account in accounts:
        print(f'Processing account ID: {account["Id"]}')
        if account['Id'] != master_session.client('sts').get_caller_identity().get('Account'):
            session = assume_role_in_account(account['Id'], master_session, args.region)
            if not session:
                print(f"Skipping account {account['Id']} due to error assuming role.")
                continue
        enable_standards(session, standards_arns)

if __name__ == "__main__":
    main()
