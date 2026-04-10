"""
This script captuires the Security Hub findings for the accounts 
belonging to the Sample Project. 

There are currently two accounts in scope:

123456789012 - myorg-project-dev
123456789012 - myorg-project-shared
"""
import boto3

# Setup the session using an SSO profile
AWS_PROFILE = "security-tooling"
boto3.setup_default_session(profile_name=AWS_PROFILE)

#establish connection to SecurityHub
securityhub = boto3.client('securityhub')

#list of accounts
account_numbers = [
    "123456789012",
    "123456789012",
]

# get findings from each account
for account in account_numbers:
    print("Getting findings from Account: ", account)
    response = securityhub.get_findings(
    Filters={
        'AwsAccountId': [
            {
                'Value': account,
                'Comparison': 'EQUALS'
            },
        ]
    })

    print(f"SecurityHub findings for account {account}:\n")
    # Loop through all findings
    for finding in response['Findings']:
        print(f"{'ID:':25}{finding['Id']:25}{'Title:' + finding['Title']:25}")
        print(f"{'Type:':25}{finding['Types'][0]:25}"
              f"{'Severity:' + finding['Severity']['Label']:25}")
        print(f"{'Description:':25}{finding['Description']:25}"
              f"{'UpdatedAt:' + str(finding['UpdatedAt']):25}")
        print("-" * 80)
print("\n")
