"""Script to export AWS Security Hub findings to an XLSX file."""

import argparse
import time
import os
from datetime import datetime
import pandas as pd
import botocore.exceptions
import boto3

def main():
    """
    Export Security Hub findings to an XLSX file.
    """
    # Create an argument parser
    parser = argparse.ArgumentParser(description='Export Security Hub findings to an XLSX file.')
    parser.add_argument('-p', '--profile', type=str, required=True,
                        help='The name of the AWS profile to use.')
    parser.add_argument('-e', '--export', type=str, required=True,
                        choices=['local', 's3_bucket'], help='The export option to use.')
    parser.add_argument('-s', '--severity', type=str,
                        choices=['INFORMATIONAL',
                                 'LOW',
                                 'MEDIUM',
                                 'HIGH',
                                 'CRITICAL'], 
                                 help='The minimum severity level of findings to export.')
    args = parser.parse_args()

    # Create a mapping of severity label names to their integer values
    severity_mapping = {
        'INFORMATIONAL': 0,
        'LOW': 1,
        'MEDIUM': 5,
        'HIGH': 8,
        'CRITICAL': 10,
    }

    # Get the current time before executing the main block of code
    start_time = time.time()

    # Create a Security Hub client with the specified profile
    session = boto3.Session(profile_name=args.profile)
    client = session.client('securityhub')

    # Create a paginator to retrieve all findings
    paginator = client.get_paginator('get_findings')
    findings = []
    for page in paginator.paginate():
        findings.extend(page['Findings'])

    # Filter the findings based on the severity level if specified
    if args.severity is not None:
        severity_value = severity_mapping[args.severity]
        findings = [f for f in findings if f['Severity']['Normalized'] >= severity_value]

    # Convert the findings to a Pandas dataframe
    findings_df = pd.DataFrame(findings)

    if args.export == 'local':
        export_local(findings_df)
    elif args.export == 's3_bucket':
        export_s3_bucket(findings_df, session)

    # Get the current time after executing the main block of code
    end_time = time.time()

    # Calculate the elapsed time and print it
    elapsed_time = (end_time - start_time) / 60
    print(f"Elapsed time: {elapsed_time:.2f} minutes")

def export_local(findings_df):
    """
    Export findings to a local XLSX file.
    """
    # Create the exports directory if it does not exist
    if not os.path.exists('exports'):
        os.makedirs('exports')

    # Generate a timestamp and format it as a string
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # Name the file with the timestamp and save it in the exports directory
    filename = f'exports/security_hub_findings_{timestamp}.xlsx'
    findings_df.to_excel(filename, index=False)

    print(f'Exported findings to {filename}')

def export_s3_bucket(findings_df, session):
    """
    Export findings to an s3_bucket bucket.
    """
    # Check if the s3_bucket bucket and folder exist, and create them if necessary
    bucket_name = 'myorg-security-hub-findings-exports'
    folder_name = 'myorg-security-hub-findings-reports'

    s3_bucket = session.client('s3_bucket')

    try:
        s3_bucket.head_bucket(Bucket=bucket_name)
    except botocore.exceptions.ClientError:
        s3_bucket.create_bucket(Bucket=bucket_name)

    try:
        s3_bucket.head_object(Bucket=bucket_name, Key=f'{folder_name}/')
    except botocore.exceptions.ClientError:
        s3_bucket.put_object(Bucket=bucket_name, Key=f'{folder_name}/')

    # Generate a timestamp and format it as a string
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # Name the file with the timestamp and save it to the s3_bucket bucket
    filename = f'security_hub_findings_{timestamp}.xlsx'
    findings_df.to_excel(filename, index=False)

    # Upload the file to the s3_bucket bucket
    s3_bucket.upload_file(filename, bucket_name, f'{folder_name}/{filename}')

    print(f'Exported findings to s3_bucket://{bucket_name}/{folder_name}/{filename}')

if __name__ == "__main__":
    main()
