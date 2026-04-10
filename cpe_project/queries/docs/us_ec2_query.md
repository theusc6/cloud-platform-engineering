# AWS Boto3 EC2 Instance Report Script

This Python script interacts with AWS services using the `boto3` library to retrieve and report information about AWS EC2 instances. It communicates with multiple AWS accounts and regions, fetches instance details, and generates a report in an Excel spreadsheet.

## Features

- Retrieves details of EC2 instances from multiple AWS accounts and regions.
- Excludes suspended accounts and generates a report for active accounts.
- Stores instance details in a pandas DataFrame.
- Generates a summary table of instance counts by platform, state, and region.
- Exports instance details and the summary table to an Excel file.

## Script Execution

1. Install the required libraries by running:

   ```python
   pip install boto3 pandas
   ```

2. Ensure your AWS credentials are properly configured. You can set up your credentials using the AWS CLI or by exporting environment variables.

3. Run the script using the following command:

   ```python
   python us_ec2_query.py --profile_name <AWS_PROFILE_NAME>
   ```

4. Replace `<AWS_PROFILE_NAME>` with the name of the AWS profile configured in your `~/.aws/config` file.

## Script Workflow

1. The script starts by parsing command line arguments to determine the master account ID, master account name, and AWS profile name.

2. It retrieves the list of accounts in the AWS organization using the provided master account session.

3. The script removes the master account from the list of accounts and excludes accounts with suspended status.

4. For each account in the list, it assumes a role in the account using the cross-account role name (`OrganizationAccountAccessRole`). It then searches for EC2 instances in specified AWS regions.

5. EC2 instances' relevant details, such as instance ID, name, state, platform, region, account ID, and private IP, are retrieved and stored in a pandas DataFrame.

6. The script generates a summary table that includes counts of instances by platform, state, and region.

7. Both the instance details DataFrame and the summary table are saved as separate sheets in an Excel file named `US_Ec2_Report-AllRegions.xlsx`.

## Functions

- `get_instance_name(instance)`: Retrieves the name of an EC2 instance from its tags.
- `find_ec2_instances(aws_region, session, account_id, account_name)`: Retrieves details of EC2 instances within a specific region for a given account.
- `get_organization_accounts(master_sess)`: Fetches a list of accounts in the AWS organization.
- `assume_role_in_account(account_id, role_name, session)`: Assumes a role in a given account and creates a new session with the assumed role's credentials.

## Notes

- Ensure that the AWS profile being used has the necessary permissions to access the AWS Organization and EC2 instances in the desired accounts and regions.
