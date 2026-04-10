"""
Checks if AWS Config is enabled in all accounts in the organization
"""

import boto3

def is_config_enabled(sts_client, account_id, role_name):
    """
    Checks if AWS Config is enabled in the specified account
    """
    try:
        assumed_role = sts_client.assume_role(
            RoleArn=f'arn:aws:iam::{account_id}:role/{role_name}',
            RoleSessionName='CheckConfigSession'
        )
    except sts_client.exceptions.ClientError as error:
        print(f"Failed to assume role in account {account_id}. Error: {error}")
        return False

    config_client = boto3.client(
        'config',
        aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
        aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
        aws_session_token=assumed_role['Credentials']['SessionToken']
    )

    response = config_client.describe_configuration_recorders()
    return bool(response['ConfigurationRecorders'])

def main():
    """
    Checks if AWS Config is enabled in all accounts in the organization.

    This function uses the master profile to initialize a session and list all accounts
    in the organization.
    It then checks if AWS Config is enabled in each account using the AWSConfigServiceRolePolicy.
    If AWS Config is not enabled, the account ID is added to a list of disabled accounts.
    Finally, the function prints the list of disabled accounts.
    """
    # Initialize a session using the master profile
    master_session = boto3.Session(profile_name='myorg-master')
    sts_client = master_session.client('sts')
    master_account_client = master_session.client('organizations')

    config_disabled_accounts = []

    # List all accounts in the organization
    paginator = master_account_client.get_paginator('list_accounts')
    for page in paginator.paginate():
        for account in page['Accounts']:
            account_id = account['Id']
            # You will need to determine the correct role assumption here:
            # 'OrganizationAccountAccessRole'
            if not is_config_enabled(sts_client, account_id, 'AWSConfigServiceRolePolicy'):
                config_disabled_accounts.append(account_id)

    print(f'Accounts without AWS Config enabled: {config_disabled_accounts}')

if __name__ == '__main__':
    main()
