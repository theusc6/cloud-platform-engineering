"""
This script allows you to export AWS Security Hub findings to an XLSX file,
optionally filtered by severity level.
"""

#!/usr/bin/env python

import argparse
from datetime import datetime
import time
import os
import pandas as pd
import boto3

# Create an argument parser
parser = argparse.ArgumentParser(description='Export Security Hub findings to an XLSX file.')
parser.add_argument('-p', '--profile', type=str, required=True,
                    help='The name of the AWS profile to use.')
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

# Create the exports directory if it does not exist
if not os.path.exists('exports'):
    os.makedirs('exports')

# Generate a timestamp and format it as a string
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

# Name the file with the timestamp and save it in the exports directory
filename = f'exports/security_hub_findings_{timestamp}.xlsx'
findings_df.to_excel(filename, index=False)

# Get the current time after executing the main block of code
end_time = time.time()

# Calculate the elapsed time and print it
elapsed_time = (end_time - start_time) / 60
print(f"Elapsed time: {elapsed_time:.2f} minutes")
