"""
https://us-west-2.console.aws.amazon.com/lambda/home?region=us-west-2#/functions/lambda-export-secuty-hub-findings?tab=code
# arn:aws:lambda:us-west-2:123456789012:function:lambda-export-secuty-hub-findings
"""

import datetime
from io import BytesIO
import pandas as pd
import boto3

def export_security_hub_findings():
    """
    This function is designed to export all Security Hub findings to an XLSX file and upload
    """
    # Create a Security Hub client
    client = boto3.client('securityhub')

    # Create a paginator to retrieve all findings
    findings = []
    paginator = client.get_paginator('get_findings')
    for page in paginator.paginate():
        findings.extend(page['Findings'])

    # Convert the findings to a Pandas DataFrame
    findings_df = pd.DataFrame(findings)

    # Generate a timestamp and format it as a string
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # Define the S3 resources
    bucket_name = 'security-hub-findings-exports'
    folder_name = 'security-hub-findings-reports/'
    filename = f'{folder_name}security_hub_findings_{timestamp}.xlsx'

    # Export the DataFrame to an XLSX file in memory
    excel_buffer = BytesIO()
    findings_df.to_excel(excel_buffer, index=False, header=True)
    excel_buffer.seek(0)
    xlsx_bytes = excel_buffer.read()

    # Create an S3 client
    s_three = boto3.client('s3')

    # Check if the bucket exists, create it if it doesn't
    existing_buckets = [bucket['Name'] for bucket in s_three.list_buckets()['Buckets']]
    if bucket_name not in existing_buckets:
        s_three.create_bucket(Bucket=bucket_name)

    # Upload the XLSX file to S3
    s_three.put_object(Bucket=bucket_name, Key=filename, Body=xlsx_bytes)

    return {
        'statusCode': 200,
        'body': 'Security Hub findings exported successfully.'
    }
