# AWS WorkSpaces Finder Script

The AWS WorkSpaces Finder script is designed to search for AWS WorkSpaces across multiple AWS accounts associated with an AWS organization. This script streamlines the process of identifying and managing WorkSpaces by providing a consolidated view of WorkSpaces information.

## Script Functionality

The script operates as follows:

1. **Retrieval of AWS Account List:** The script begins by retrieving a list of all AWS accounts within the AWS organization. This list includes the account ID, account name, and other attributes of each account.

2. **Assuming Roles:** To gain access to each AWS account, the script assumes a role in each account. This role provides the necessary permissions to search for and retrieve information about WorkSpaces in that account.

3. **WorkSpace Identification:** The script searches for WorkSpaces in each AWS account across multiple regions. For each WorkSpace found, it fetches information such as Workspace ID, Directory ID, User Name, State, and Region.

4. **Data Compilation and Reporting:** The information about each WorkSpace is stored in a structured pandas DataFrame. Once the script has searched all accounts and regions, it compiles the WorkSpaces data into an Excel file. The Excel file includes two sheets: "WorkSpaces Details" and "Summary."

5. **Summary Table:** The "Summary" sheet in the Excel file contains a summary table that lists the number of WorkSpaces found in each account. This summary provides a quick overview of WorkSpaces distribution across different accounts.

## Prerequisites

- Ensure that your AWS credentials are properly configured. You can use the AWS CLI or set environment variables to configure your credentials.

## Script Execution

1. Install the required Python packages using the following command:

   ```python
   pip install boto3 argparse pandas
   ```

2. Run the script from the command line using the following command:

   ```python
   python us_workspaces_query.py --profile_name <AWS_PROFILE_NAME>
   ```

   Replace `<AWS_PROFILE_NAME>` with the name of the AWS CLI profile you want to use for authentication.

## Command Line Arguments

The script accepts the following command line arguments:

- `--master_account_id`: The AWS account ID of the master account in the AWS organization.
- `--master_account_name`: The name of the master account in the AWS organization.
- `--profile_name`: The AWS CLI profile to use for authenticating with AWS.

## Dependencies

The script uses the Boto3 AWS SDK for Python to interact with AWS services. It requires the following Python packages: `boto3`, `argparse`, and `pandas`.

## Note

- Ensure that the AWS profile you provide has the necessary permissions to access the AWS organization, WorkSpaces, and the relevant regions.
- The script will generate an Excel file named `WorkSpaces_Report-AllAccounts.xlsx` containing detailed information about the identified WorkSpaces and a summary table.
