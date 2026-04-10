# AWS ACM Certificate Report Generator

This script is designed to generate a report of AWS ACM (AWS Certificate Manager) certificates across multiple AWS accounts and regions. It utilizes the `boto3` library to interact with AWS services and `pandas` library for data processing and Excel export.

## Purpose

The purpose of this script is to provide an organized report of ACM certificates within an AWS organization. It includes details such as the certificate's domain name, status, days to expiry, validation method, account ID, and region. The report is saved in an Excel file named `US_ACM_Certificate_Report-AllRegions.xlsx`.

## Features

- Fetches a list of accounts from an AWS organization.
- Iterates through accounts and regions to search for ACM certificates.
- Retrieves and processes ACM certificate details.
- Creates summary tables for the total number of certificates and certificates by validation method.
- Applies conditional formatting to highlight certificates with 30 or fewer days to expiry.

## Usage

1. Ensure that you have `boto3`, `pandas`, and `xlsxwriter` libraries installed. You can install them using the following command:

   ```python
   pip install boto3 pandas xlsxwriter
   ```

2. Run the script using the command:

   ```python
   python us_acm_query.py --master_account_id <MASTER_ACCOUNT_ID> --master_account_name <MASTER_ACCOUNT_NAME> --profile_name <AWS_PROFILE_NAME>
   ```

   Replace `<MASTER_ACCOUNT_ID>` with the ID of the AWS master account, `<MASTER_ACCOUNT_NAME>` with the name of the master account, and `<AWS_PROFILE_NAME>` with the AWS CLI profile name.

3. The script will generate a report named `US_ACM_Certificate_Report-AllRegions.xlsx` containing ACM certificate details and summary tables.

## Note

Please ensure that your AWS IAM permissions are properly configured to allow the required actions for the script to access ACM certificates and other necessary resources.

## Author

This script was written by [user](https://github.com/user). Feel free to contact the author for any questions or improvements related to this script.
