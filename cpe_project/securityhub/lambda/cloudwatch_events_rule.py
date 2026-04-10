"""
This script is designed to create an AWS CloudWatch Event Rule for automating the execution
of the SecurityHub findings export Lambda function. The rule is scheduled to run on the 
first day of every month at midnight. The script also adds an event target to the rule, 
specifying the Lambda function that will be triggered by the rule.
"""

import boto3

# Initialize the AWS CloudWatch Events client
client = boto3.client('events')

# Define the rule name and description
RULE_NAME = 'Export-Security-Hub-Findings-Monthly'
RULE_DESCRIPTION = '''
Runs the SecurityHub findings export Lambda function on the first of every month at midnight
'''

# Create the CloudWatch Event Rule
response = client.put_rule(
    Name=RULE_NAME,
    Description=RULE_DESCRIPTION,
    ScheduleExpression='cron(0 0 1 * ? *)',  # Run on the first day of every month at midnight
    State='ENABLED'
)

if response['ResponseMetadata']['HTTPStatusCode'] == 200:
    print(f"Rule '{RULE_NAME}' created successfully.")

# Add an event target to the rule
LAMBDA_ARN = 'arn:aws:lambda:us-west-2:123456789012:function:lambda-export-secuty-hub-findings'

response = client.put_targets(
    Rule=RULE_NAME,
    Targets=[
        {
            'Id': 'SecurityHubFindingsExport',
            'Arn': LAMBDA_ARN
        }
    ]
)

if response['FailedEntryCount'] == 0:
    print(f"Event target added to rule '{RULE_NAME}' successfully.")
