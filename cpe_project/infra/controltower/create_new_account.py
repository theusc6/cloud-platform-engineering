"""
Create an AWS account in ControlTower AccountFactory and verify it in AWS Organizations.

Args:
    profile (str): AWS profile name to use for the operation.
    account_data (dict): Dictionary containing account information.
        - 'account_email' (str): Account email address.
        - 'display_name' (str): Display name for the account.
        - 'ou_name' (str): Organization Unit name.

Returns:
    None
"""

import argparse
import time
import boto3
import botocore

def is_account_valid(organizations_client, account_email):
    """
    Check if the account with the specified email address already exists in the AWS Organization.
    """
    try:
        response = organizations_client.list_accounts()
        existing_accounts = response['Accounts']

        for account in existing_accounts:
            if account['Email'] == account_email:
                return False  # Account email is already in use

        return True  # Account email is not in use

    except botocore.exceptions.ClientError:
        return False  # Error occurred while checking, consider it as not valid

def create_aws_account(profile, account_data):
    """
    Create an AWS account in ControlTower AccountFactory and verify it in AWS Organizations.
    """

    # Initialize the AWS session with the specified profile
    session = boto3.Session(profile_name=profile)

    # Initialize the AWS ControlTower client
    controltower_client = session.client('controltower')

    # Extract account information from the input data
    account_email = account_data['account_email']
    display_name = account_data['display_name']
    iam_identity_email = "user@example.com"  # Confirm this IAM identity email
    iam_identity_name = "user"  # Confirm this IAM identity name
    ou_name = account_data['ou_name']

    try:
        # Create a new account in AWS ControlTower AccountFactory
        response = controltower_client.create_account(
            AccountName=display_name,
            AccountEmail=account_email,
            RoleName=iam_identity_name,
            RoleEmail=iam_identity_email,
            OrganizationUnitName=ou_name
        )

        print(f"Account {display_name} with email {account_email} creation initiated successfully.")

        # Wait for a few seconds to allow AWS ControlTower to process the request
        time.sleep(5)

        # Verify the account in AWS Organizations
        organizations_client = session.client('organizations')
        response = organizations_client.describe_account(AccountId=response['AccountId'])
        print(f"Account {display_name} with email {account_email} verified in AWS Organizations.")

    except botocore.exceptions.ClientError as error:
        error_code = error.response.get('Error', {}).get('Code')
        error_message = error.response.get('Error', {}).get('Message')
        print(f"Failed to create account {display_name} with email {account_email}. Error code: {error_code}, Message: {error_message}")

def main():
    """
    Main function.
    """
    parser = argparse.ArgumentParser(description='Create an AWS account in ControlTower AccountFactory and verify in Organizations')
    parser.add_argument('--profile', required=True, help='AWS profile name to use for the operation')
    parser.add_argument('--account_email', required=True, help='Account email address')
    parser.add_argument('--display_name', required=True, help='Display name for the account')
    parser.add_argument('--ou_name', required=True, help='Organization Unit name')

    args = parser.parse_args()

    # Prepare account data from command line arguments
    account_data = {
        'account_email': args.account_email,
        'display_name': args.display_name,
        'ou_name': args.ou_name
    }

    # Create AWS account and verify in AWS Organizations
    create_aws_account(args.profile, account_data)

if __name__ == '__main__':
    main()
