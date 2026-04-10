"""
https://us-west-2.console.aws.amazon.com/lambda/home?region=us-west-2#/functions/lambda-export-secuty-hub-findings?tab=code
arn:aws:lambda:us-west-2:123456789012:function:lambda-export-secuty-hub-findings

Note 1: Be sure to replace the account number to reflect that of 
the Security Hub Delegated Administrator.

Note 2: Be sure to add the correct layer to the Lambda function in order to support Pandas.
AWSSDKPandas-Python311 is the current version and what is deployed with the deployment code.

Note 3: A second layer must be added for xlsxwriter. This will be a custom layer and the current 
version will be included in deployment code as well. New versions must be generated as needed.

Note 4: This function will typically require a timeout of 5 minutes and memory of 256.
"""

from datetime import datetime
import json
import io
import pandas as pd
import boto3
from botocore.exceptions import ClientError

def create_s3_bucket(bucket_name):
    """
    This function creates an Amazon S3 bucket with a specified name, policy, tagging,
    versioning configuration, public access block configuration, and lifecycle policy.

    Parameters:
    session (boto3.Session): An AWS session object created by Boto3.
    bucket_name (str): The name of the S3 bucket to be created.
    account_id (str): The AWS account ID in which the S3 bucket will be created.
    region (str): The AWS region where the S3 bucket will be created.

    Returns:
    None
    """
    s3_client = boto3.client('s3')

    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
                    {
            'Sid': 'RequireSSLOnly',
            'Effect': 'Deny',
            'Principal': '*',
            'Action': 's3:*',
            'Resource': [
                f'arn:aws:s3:::{bucket_name}/*',
                f'arn:aws:s3:::{bucket_name}'
            ],
            'Condition': {
                'Bool': {
                    'aws:SecureTransport': 'false'
                }
            }
        }

        ]
    }

    try:
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': "us-west-2"}
        )
        print(f"{bucket_name} has now been created.")
    except ClientError as client_error:
        if client_error.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print(f"Bucket {bucket_name} already exists.")
        else:
            print(f"An error occurred while creating the bucket: "
                  f"{client_error.response['Error']['Message']}")
            return

    try:
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )
        print(f"SSL is now required for bucket {bucket_name}.")
    except ClientError as client_error:
        print(f"An error occurred while applying the bucket policy: "
              f"{client_error.response['Error']['Message']}")

    try:
        s3_client.put_bucket_tagging(
            Bucket=bucket_name,
            Tagging={'TagSet': [{'Key': 'Category', 'Value': 'Security'}]}
        )
        print(f"Tags have been applied to bucket {bucket_name}.")
    except ClientError as client_error:
        print(f"An error occurred while applying bucket tags: "
              f"{client_error.response['Error']['Message']}")

    try:
        s3_client.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={
                    'Status': 'Enabled'
                }
            )
        print(f"Versioning is enabled for for {bucket_name}.")
    except ClientError as client_error:
        print(f"An error occurred while enabling bucket versioning: "
              f"{client_error.response['Error']['Message']}")

    try:
        s3_client.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
        print(f"Public access is blocked for {bucket_name}.")
    except ClientError as client_error:
        print(f"An error occurred while blocking public access: "
              f"{client_error.response['Error']['Message']}")

    lifecycle_policy = {
        'Rules': [
            {
                'ID': 'myorg-securityhub-s3.13-default-lifecycle-policy',
                'Status': 'Enabled',
                'Filter': {
                    'Prefix': ''
                },
                'Transitions': [
                    {
                        'Days': 0,
                        'StorageClass': 'INTELLIGENT_TIERING'
                    }
                ],
                'NoncurrentVersionTransitions': [
                    {
                        'NoncurrentDays': 30,
                        'StorageClass': 'GLACIER_IR'
                    }
                ],
                'Expiration': {
                    'ExpiredObjectDeleteMarker': True
                },
                'NoncurrentVersionExpiration': {
                    'NoncurrentDays': 180,
                    'NewerNoncurrentVersions':1
                },
                'AbortIncompleteMultipartUpload': {
                    'DaysAfterInitiation': 30
                }
            }
        ]
    }

    log_bucket_name= "myorg-securityhub-s3.9accesslogging-123456789012-us-west-2"

    try:
        s3_client.put_bucket_lifecycle_configuration(
            Bucket=bucket_name,
            LifecycleConfiguration=lifecycle_policy
        )
        print(f"Applied bucket lifecycle policy for bucket {bucket_name}.")
    except ClientError as client_error:
        print(f"An error occurred while applying lifecycle policy: "
              f"{client_error.response['Error']['Message']}")

    if 'myorg-securityhub-s3.9accesslogging' not in bucket_name:
        try:
            s3_client.put_bucket_logging(
                Bucket=bucket_name,
                BucketLoggingStatus={
                    'LoggingEnabled': {
                        'TargetBucket': log_bucket_name,
                        'TargetPrefix': f"{bucket_name}/"
                    }
                }
            )
            print(f"Enabled logging for bucket {bucket_name}. "
                  f"Logging to {log_bucket_name}.")
        except ClientError as error:
            print(f"An error occurred: {error.response['Error']['Message']}")

def filter_findings(findings):
    """
    Filter findings based on specific criteria.

    This function filters the provided list of findings. It selects findings where:
    - The product name is 'Security Hub' and the compliance status is 'FAILED'.
    - The product name is not 'Security Hub'.

    Parameters:
    findings (list): A list of findings (dictionaries) to be filtered.

    Returns:
    list: A filtered list of findings based on the defined criteria.
    """
    filtered_findings = []
    for finding in findings:
        # Check if the product is Security Hub and the compliance status is FAILED
        if finding.get('ProductName', '') == 'Security Hub' and \
           finding.get('Compliance', {}).get('Status', '') == 'FAILED':
            filtered_findings.append(finding)
        # If the product is not Security Hub, include it regardless of the compliance status
        elif finding.get('ProductName', '') != 'Security Hub':
            filtered_findings.append(finding)

    return filtered_findings


def process_findings_data(findings_df):
    """
    Process and clean findings data.

    This function processes a DataFrame containing Security Hub findings. It performs the following:
    - Updates the 'Severity' column to display the 'Label' value, or 'Unknown' if not available.
    - Cleans up the 'Types' column by removing specific characters.
    - Drops unnecessary columns.

    Parameters:
    findings_df (pandas.DataFrame): A DataFrame containing findings data to be processed.

    Returns:
    pandas.DataFrame: The processed DataFrame with cleaned and formatted data.
    """
    if 'Severity' in findings_df.columns:
        findings_df['Severity'] = findings_df['Severity'].apply(lambda x: x.get('Label', 'Unknown'))

    findings_df['Types'] = findings_df['Types'].astype(str)
    findings_df['Types'] = findings_df['Types'].str.replace("['", '', regex=False)
    findings_df['Types'] = findings_df['Types'].str.replace("']", '', regex=False)

    columns_to_drop = ['Sample', 'SourceUrl', 'FindingProviderFields', 'GeneratorId', 'NetworkPath']
    findings_df.drop(columns_to_drop, axis=1, errors='ignore')
    return findings_df

def write_findings_to_excel(findings_df):
    """
    Writes the findings data to an Excel format.

    This function takes a DataFrame of Security Hub findings and writes it to an Excel format
    using a BytesIO stream. This stream is then used to create the Excel file content.

    Parameters:
    findings_df (pandas.DataFrame): A DataFrame containing the findings to be written to Excel.

    Returns:
    bytes: The Excel file content in a binary format.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer: # pylint: disable=abstract-class-instantiated
        findings_df.to_excel(writer, sheet_name='Findings', index=False)
    return output.getvalue()

def get_summary_df(group, final_columns, final_index):
    """
    Creates a summary DataFrame for a specific group of findings.

    This function aggregates findings for each product and severity level within a group.
    It calculates the count of findings per product and severity, then compiles these counts
    into a summary DataFrame. The function also calculates the total findings
    for each severity level.

    Parameters:
    group (pd.DataFrame): A DataFrame representing a group of findings, typically grouped by
    account ID.
    final_columns (list): List of columns (product names) to be included in the summary DataFrame.
    final_index (list): List of index labels (severity levels) for the summary DataFrame.

    Returns:
    pd.DataFrame: A DataFrame containing the summarized count of findings per
    product and severity level,along with the total findings for each severity level.
    """
    summary_df = pd.DataFrame(0, index=final_index, columns=final_columns)
    for product in final_columns:
        for severity in final_index[:-1]:
            condition = (group['Severity'] == severity) & \
                        (group['ProductName'].str.contains(product, case=False))
            count = len(group[condition])
            summary_df.loc[severity, product] = count
    summary_df['Total Findings'] = summary_df.sum(axis=1)
    return summary_df

def calculate_totals(summary_df, final_columns, final_index):
    """
    Calculates the total findings per severity and total per product.

    Parameters:
    summary_df (pd.DataFrame): The DataFrame containing the summarized findings.
    final_columns (list): The list of columns to sum across.
    final_index (list): The list of index labels to ensure the correct row order.

    Returns:
    pd.DataFrame: The updated DataFrame with totals calculated.
    """
    # Calculate row totals
    summary_df['Total Findings'] = summary_df[final_columns].sum(axis=1)

    # Calculate column totals
    total_per_product = summary_df.loc[final_index[:-1], final_columns].sum()
    summary_df.loc['Total', final_columns] = total_per_product

    # Calculate grand total
    summary_df.loc['Total', 'Total Findings'] = total_per_product.sum()

    # Reindex to ensure the rows are in the correct order
    summary_df = summary_df.reindex(final_index)

    return summary_df

def write_summary_to_excel(writer, grouped, final_columns, final_index, bold_italic_format):
    """
    Writes the summary of findings to an Excel sheet.
    
    This function takes grouped findings, iterates through each group, and compiles
    a summary DataFrame.

    The summary is then written to an Excel writer object. The function handles formatting and
    writes account-wise and final summaries to the Excel sheet.

    Parameters:
    writer (pd.ExcelWriter): The Excel writer object used for writing the DataFrame.
    grouped (pd.GroupBy): Grouped DataFrame of Security Hub findings by account ID.
    final_columns (list): List of columns to be included in the summary DataFrame.
    final_index (list): List of index labels for the summary DataFrame.
    bold_italic_format (xlsxwriter.Format): Format object for styling the Excel sheet.

    Returns:
    None
    """
    start_row = 2
    sheet_name = 'Summary'
    final_summary_df = pd.DataFrame(0, index=final_index, columns=final_columns)

    for account_id, group in grouped:
        # Calculate summary for each account
        summary_df = get_summary_df(group, final_columns, final_index)
        summary_df = calculate_totals(summary_df, final_columns, final_index)

        # Write individual account summary with totals to Excel
        summary_df.to_excel(writer, sheet_name=sheet_name, startrow=start_row, index=True)
        worksheet = writer.sheets[sheet_name]
        worksheet.write(start_row - 1, 0, f'Account ID: {account_id}', bold_italic_format)

        # Update the starting row for the next account summary
        start_row += len(summary_df) + 3

        # Add the account summary to the final summary
        final_summary_df = final_summary_df.add(summary_df.drop('Total'), fill_value=0)

    # Calculate totals for the final summary across all accounts
    final_summary_df = calculate_totals(final_summary_df, final_columns, final_index)

    # Write final summary to Excel
    final_summary_df.to_excel(writer, sheet_name=sheet_name, startrow=start_row, index=True)
    worksheet.write(start_row - 1, 0, 'Final Summary Across All Accounts', bold_italic_format)

def export_security_hub_findings(bucket_name):
    """
    Exports Security Hub findings to an Excel file and uploads it to S3.

    This function fetches Security Hub findings using the AWS Security Hub client,
    processes these findings, and writes them to an Excel file.
    The Excel file is then uploaded to an S3 bucket. The function
    handles the creation of a paginated request to handle large numbers of findings.

    Parameters:
    bucket_name (str): The name of the S3 bucket where the Excel file will be stored.

    Returns:
    dict: A dictionary with the status code and a message indicating the success of the operation.
    """
    # Define final columns and index
    final_columns = ['Inspector', 'Security Hub', 'GuardDuty', 'Health']
    final_index = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'Total']

    # Rest of your code...
    client = boto3.client('securityhub')
    filters = {
        'RecordState': [{'Value': 'ACTIVE', 'Comparison': 'EQUALS'}],
        'WorkflowStatus': [{'Value': 'NEW', 'Comparison': 'EQUALS'}],
        'ProductName': [
            {'Value': 'Security Hub', 'Comparison': 'EQUALS'},  # Adjust values based on exact product names
            {'Value': 'GuardDuty', 'Comparison': 'EQUALS'},
            {'Value': 'Health', 'Comparison': 'EQUALS'},
            {'Value': 'Config', 'Comparison': 'EQUALS'},
            {'Value': 'Systems Manager Patch Manager', 'Comparison': 'EQUALS'},
            {'Value': 'IAM Access Analyzer', 'Comparison': 'EQUALS'}
        ]
    }
    
    findings = []
    for page in client.get_paginator('get_findings').paginate(Filters=filters):
        findings.extend(page['Findings'])

    filtered_findings = filter_findings(findings)
    findings_df = pd.DataFrame(filtered_findings)
    processed_findings_df = process_findings_data(findings_df)

    grouped = processed_findings_df.groupby('AwsAccountId')
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:  # pylint: disable=abstract-class-instantiated
        processed_findings_df.to_excel(writer, sheet_name='Instance Details', index=False)
        bold_italic_format = writer.book.add_format({'bold': True, 'italic': True})
        write_summary_to_excel(writer, grouped, final_columns, final_index, bold_italic_format)

    xlsx_data = output.getvalue()
    upload_to_s3(bucket_name, xlsx_data)

def upload_to_s3(bucket_name, xlsx_data):
    """
    Uploads the the final report in Excel to S3.
    """
    s3_client = boto3.client('s3')
    timestamp = datetime.now()
    year_folder = timestamp.strftime('%Y')
    month_folder = timestamp.strftime('%m')
    filename = (
        f'security-hub-findings-reports/{year_folder}/{month_folder}/'
        f'security_hub_findings_{timestamp.strftime("%Y-%m-%d_%H-%M-%S")}.xlsx'
    )
    s3_client.put_object(Bucket=bucket_name, Key=filename, Body=xlsx_data)

def main(event, context): # pylint: disable=unused-argument
    """
    Main function of script
    """
    bucket_name = 'myorg-securityhub-s3-findings-report-123456789012-us-west-2'
    export_security_hub_findings(bucket_name)

if __name__ == '__main__':
    main() # pylint: disable=no-value-for-parameter
