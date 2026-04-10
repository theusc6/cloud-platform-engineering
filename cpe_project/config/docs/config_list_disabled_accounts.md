
# Check AWS Config Status Across AWS Organization

## Overview

This Python script checks if AWS Config is enabled in all AWS accounts that are part of an AWS Organization. It operates from a 'master' account, leveraging the AWS Organizations and STS (Security Token Service) to assume roles in each member account and query the state of AWS Config service. 

## Prerequisites

- AWS CLI and Boto3 installed
- AWS Credentials set up for the master account under a profile named `myorg-master`
    - **NOTE:** Change this to whatever you have sconfigured for this account in your local .aws/config file.

## Usage

1. Clone the repository.
2. Navigate to the directory where the script resides.
3. Run `python config_list_disabled_accounts.py` from the command line.

The script will print the AWS Account IDs where AWS Config is not enabled.

## How It Works

1. The script initializes a session using a specified master profile, in this case, `myorg-master`.
2. This expects that you are already logged in to the `myorg-mater` AWS Account.
    - `master_session = boto3.Session(profile_name='myorg-master')`
3. It then lists all accounts in the AWS Organization.
4. For each account, it assumes a role (`AWSConfigServiceRolePolicy` or a role you specify) to initialize a temporary session.
5. Utilizes this temporary session to check if AWS Config is enabled.
6. Stores the Account IDs where AWS Config is not enabled in a list and then prints this list.

## How to Extend

1. **Custom Roles**: If your organization uses custom roles that the master account can assume, you can modify the `role_name` parameter in the `is_config_enabled` function.
2. **Additional Checks**: The script can be extended to check other services, not just AWS Config. Add additional functions and integrate them into the `main()` loop.
3. **Error Handling**: Add more specific error-handling for different kinds of exceptions that could be encountered during role assumption or while interacting with AWS services.
4. **Reporting**: Integrate with a reporting tool to generate more complex reports based on the findings.
5. **Automated Remediation**: Extend the script to enable AWS Config automatically in accounts where it is disabled.
