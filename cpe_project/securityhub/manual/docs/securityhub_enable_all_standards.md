# AWS Security Hub Standards Enabler

## Overview
This module provides a script to enable specific security standards in AWS Security Hub for accounts in an AWS Organization. The script can target a specific account or all accounts in the organization and can be executed for a specific AWS region.

## Functions
get_organization_accounts(master_sess):

### Retrieves a list of accounts in the AWS Organization.
Args: A boto3 Session object for the master account.
Returns: A list of dictionaries containing account information, including the account's ID and name.
assume_role_in_account(account_id, session, region_name):

### Assumes a role in the given account and creates a new session with the assumed role's credentials.
Args: Account ID, existing boto3 session, and region name.
Returns: A new boto3 Session object with the assumed role's credentials, or None if an error occurred.
enable_standards(session, standards_arns):

### Enables the specified security standards in AWS Security Hub for a given session.
Args: A boto3 Session object and a list of ARNs representing the security standards to be enabled.
Note: Any errors encountered will be printed to the console.
parse_arguments():

### Parses command-line arguments for AWS profile name, region, and account ID.
Returns: Parsed arguments containing profile_name, region, and account_id.
main():

### Main function to coordinate the enabling of security standards.

The script can be executed from the command line with the following syntax:

python securityhub_enable_all_standards.py `--profile_name` <AWS profile name> `--region` <AWS region> [`--account_id` <AWS account ID>]

_**If the account_id argument is omitted, the script will process all accounts in the organization.**_

## Additional Information
The script is designed to automate the process of enabling security standards across multiple AWS accounts within an organization. The standards can be specified using Amazon Resource Names (ARNs), and the script can operate on a specific region across all accounts in the organization. Utilizing the script can help ensure consistent security configurations across an organization and facilitate compliance with various security frameworks and regulations.
