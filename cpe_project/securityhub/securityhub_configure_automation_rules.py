"""
This module defines rules for SecurityHub and includes functions to create
automation rules in AWS. It allows suppression of findings and other automated
actions based on specified criteria.

To use this module, provide the appropriate AWS profile and region as command-line
arguments. The rules defined in the `rules` list will be created in the specified
AWS account and region.

As new rules need to be added, simply add them within the 'rules' list.
"""
import argparse
import boto3
from botocore.exceptions import ClientError

rules = [
    {
        'RuleStatus':'ENABLED',
        'RuleOrder':1,
        'RuleName':"Finding Suppression - CloudTrail should have encryption at-rest enabled "
        "- AWS Control Tower Resources ONLY",
        'Description':"AWS Control Tower resources should not be modified, per SCP & "
        "AWS Best Practices. Although the CloudTrails themsevles are not encrypted, "
        "the S3 buckets are encrypted using Server-side encryption with Amazon S3 "
        "managed keys (SSE-S3).\n",
        'IsTerminal':False,
        'Criteria': 
        {
            'Title': [
                {
                'Value' : '2.7 Ensure CloudTrail logs are encrypted at rest using KMS CMKs',
                'Comparison': 'EQUALS'
                },
                {
                'Value' : '3.7 Ensure CloudTrail logs are encrypted at rest using KMS CMKs',
                'Comparison': 'EQUALS'
                },
                {
                'Value' : 'PCI.CloudTrail.1 CloudTrail logs should be encrypted at '
                'rest using AWS KMS CMKs',
                'Comparison': 'EQUALS'
                },
                {
                'Value' : 'CloudTrail.2 CloudTrail should have encryption at-rest enabled',
                'Comparison': 'EQUALS'
                },
            ],
            'ResourceId': [
                {
                'Value' : 'aws-controltower-BaselineCloudTrail',
                'Comparison': 'CONTAINS'
                }
            ],
        },
        'Actions': [
        {
            'Type': 'FINDING_FIELDS_UPDATE',
            'FindingFieldsUpdate':{
                'Workflow': {
                    'Status': 'SUPPRESSED'
                }
            }
        }
        ]
    },
    {
        'RuleStatus':'ENABLED',
        'RuleOrder':2,
        'RuleName':"Finding Suppression - Unused EC2 security groups should be removed",
        'Description':"Disabled in this account and region on August 2, 2023 \n \n Reason "
         "for disabling: https://example.atlassian.net/",
        'IsTerminal':False,
        'Criteria':
        {
            'Title': [
                {
                'Value' : 'EC2.22 Unused EC2 security groups should be removed',
                'Comparison': 'EQUALS'
                },
            ],
        },
        'Actions': [
        {
            'Type': 'FINDING_FIELDS_UPDATE',
            'FindingFieldsUpdate':{
                'Workflow': {
                    'Status': 'SUPPRESSED'
                }
            }
        }
        ]

    },
    {
        'RuleStatus':'ENABLED',
        'RuleOrder':3,
        'RuleName':"Finding Suppression - CloudFormation stacks should be integrated "
        "with Simple Notification Service (SNS) - AWS Control Tower Resources ONLY",
        'Description':"AWS Control Tower resources should not be modified, per SCP & "
        "AWS Best Practices.",
        'IsTerminal':False,
        'Criteria':
        {
            'Title': [
                {
                'Value' : 'CloudFormation.1 CloudFormation stacks should be integrated '
                'with Simple Notification Service (SNS)',
                'Comparison': 'EQUALS'
                },
            ],
            'ResourceId': [
                {
                'Value' : 'AWSControlTower',
                'Comparison': 'CONTAINS'
                }
            ]
        },
        'Actions': [
        {
            'Type': 'FINDING_FIELDS_UPDATE',
            'FindingFieldsUpdate':{
                'Workflow': {
                    'Status': 'SUPPRESSED'
                }
            }
        }
        ]

    },
    {
        'RuleStatus':'ENABLED',
        'RuleOrder':4,
        'RuleName':"Finding Suppression - S3 buckets should have event notifications enabled",
        'Description':"Disabled in this account and region on August 2, 2023\n\nReason for "
        "disabling: https://example.atlassian.net/",
        'IsTerminal':False,
        'Criteria':
        {
            'Title': [
                {
                'Value' : 'S3.11 S3 buckets should have event notifications enabled',
                'Comparison': 'EQUALS'
                },
            ],
        },
        'Actions': [
        {
            'Type': 'FINDING_FIELDS_UPDATE',
            'FindingFieldsUpdate':{
                'Workflow': {
                    'Status': 'SUPPRESSED'
                }
            }
        }
        ]

    },
    {
        'RuleStatus':'ENABLED',
        'RuleOrder':5,
        'RuleName':"Finding Suppression - Hardware MFA should be enabled for the root user",
        'Description':"Disabled in this account and region on December 2, 2022 \n \n Reason "
        "for disabling: MyOrg does not have a standard for Hardware MFA",
        'IsTerminal':False,
        'Criteria':
        {
            'Title': [
                {
                'Value': 'IAM.6 Hardware MFA should be enabled for the root user',
                'Comparison': 'EQUALS'
                },
                {
                'Value': 'PCI.IAM.4 Hardware MFA should be enabled for the root user',
                'Comparison': 'EQUALS'
                },
                {
                'Value': '1.14 Ensure hardware MFA is enabled for the root user',
                'Comparison': 'EQUALS'
                },
                {
                'Value': "1.6 Ensure hardware MFA is enabled for the 'root' user account",
                'Comparison': 'EQUALS'
                },
            ],
        },
        'Actions': [
        {
            'Type': 'FINDING_FIELDS_UPDATE',
            'FindingFieldsUpdate':{
                'Workflow': {
                    'Status': 'SUPPRESSED'
                }
            }
        }
        ]
    },
    {
        'RuleStatus':'ENABLED',
        'RuleOrder':6,
        'RuleName':"Finding Suppression - S3 bucket server access logging should be enabled",
        'Description':"Marks findings for target logging buckets as suppressed.",
        'IsTerminal':False,
        'Criteria':
        {
            'Title': [
                {
                'Value': 'S3.9 S3 bucket server access logging should be enabled',
                'Comparison': 'EQUALS'
                },
            ],
            'ResourceId': [
                {
                'Value' : 'myorg-securityhub-s3.9accesslogging-',
                'Comparison': 'CONTAINS'
                }
            ]

        },
        'Actions': [
        {
            'Type': 'FINDING_FIELDS_UPDATE',
            'FindingFieldsUpdate':{
                'Workflow': {
                    'Status': 'SUPPRESSED'
                }
            }
        }
    ]
    },
    {
        'RuleStatus':'ENABLED',
        'RuleOrder':7,
        'RuleName':"Finding Suppression - S3 buckets should be configured to use Object Lock",
        'Description':"No current regulatory requirement for WORM storage has been defined. \n \n "
        "Object Lock configuration changes cannot be made after bucket creation. \n \n "
        "This will undergo full EA review at a later date.",
        'IsTerminal':False,
        'Criteria':
        {
            'Title': [
                {
                'Value': 'S3.15 S3 buckets should be configured to use Object Lock',
                'Comparison': 'EQUALS'
                },
            ],
        },
        'Actions': [
        {
            'Type': 'FINDING_FIELDS_UPDATE',
            'FindingFieldsUpdate':{
                'Workflow': {
                    'Status': 'SUPPRESSED'
                }
            }
        }
        ],
    },
    {
        'RuleStatus':'ENABLED',
        'RuleOrder':8,
        'RuleName':"Finding Suppression - S3 buckets should have cross-region replication enabled",
        'Description':"This is not an explicit security requirement. In addition, \n \n "
        "it comes at additional cost and configuration. \n \n "
        "This control is pending EA design and implementation plan for BC/DR/redunduncy.",
        'IsTerminal':False,
        'Criteria':
        {
            'Title': [
                {
                'Value': 'S3.7 S3 buckets should have cross-region replication enabled',
                'Comparison': 'EQUALS'
                },
                {
                'Value': 'PCI.S3.3 S3 buckets should have cross-region replication enabled',
                'Comparison': 'EQUALS'
                },
            ],
        },
        'Actions': [
        {
            'Type': 'FINDING_FIELDS_UPDATE',
            'FindingFieldsUpdate':{
                'Workflow': {
                    'Status': 'SUPPRESSED'
                }
            }
        }
        ],
    },
    {
        'RuleStatus':'ENABLED',
        'RuleOrder':9,
        'RuleName':"Finding Suppression - Logging of delivery status should be enabled for "
        "notification messages sent to a topic - AWS Control Tower Resources ONLY",
        'Description':"AWS Control Tower resources should not be \n \n "
        "modified, per SCP & AWS Best Practices.",
        'IsTerminal':False,
        'Criteria':
        {
            'Title': [
                {
                'Value': 'SNS.2 Logging of delivery status should be enabled '
                'for notification messages sent to a topic',
                'Comparison': 'EQUALS'
                }
            ],
            'ResourceId': [
                {
                'Value' : 'aws-controltower-SecurityNotifications',
                'Comparison': 'CONTAINS'
                }
            ]
        },
        'Actions': [
        {
            'Type': 'FINDING_FIELDS_UPDATE',
            'FindingFieldsUpdate':{
                'Workflow': {
                    'Status': 'SUPPRESSED'
                }
            }
        }
        ],
    },
    {
        'RuleStatus':'ENABLED',
        'RuleOrder':10,
        'RuleName':"Finding Suppression - S3 buckets should be encrypted at rest with AWS KMS keys",
        'Description':"S3 buckets are encrypted by server-side encryption \n \n "
        " with Amazon S3 managed keys (SSE-S3).",
        'IsTerminal':False,
        'Criteria':
        {
            'Title': [
                {
                'Value': 'S3.17 S3 buckets should be encrypted at rest with AWS KMS keys',
                'Comparison': 'EQUALS'
                }
            ]
        },
        'Actions': [
        {
            'Type': 'FINDING_FIELDS_UPDATE',
            'FindingFieldsUpdate':{
                'Workflow': {
                    'Status': 'SUPPRESSED'
                }
            }
        }
        ],
    },
    {
        'RuleStatus':'ENABLED',
        'RuleOrder':11,
        'RuleName':"Finding Suppression - CloudFormation stacks should be integrated with Simple "
        "Notification Service (SNS) - All Resource Types",
        'Description':"This finding, while operationally useful for certain stacks and in \n \n "
        "certain circumstances, does not have an immediate security impact given the \n \n "
        "presence of other controls (i.e. logging, application-specific alerting, SRE \n \n "
        "efforts, etc.). Additionally, to resolve will \n \n "
        "require a concerted effort from operational and application \n \n "
        "teams that, given current resource constraints and \n \n "
        "operational activities, is not priority at this time \n \n "
        "as other measures are / or can be in place that will help to monitor the \n \n "
        "health and activity of CloudFormation stacks.",
        'IsTerminal':False,
        'Criteria':
        {
            'Title': [
                {
                'Value': 'CloudFormation.1 CloudFormation stacks should be integrated '
                'with Simple Notification Service (SNS)',
                'Comparison': 'EQUALS'
                }
            ]
        },
        'Actions': [
        {
            'Type': 'FINDING_FIELDS_UPDATE',
            'FindingFieldsUpdate':{
                'Workflow': {
                    'Status': 'SUPPRESSED'
                }
            }
        }
        ],
    },
    {
        'RuleStatus':'ENABLED',
        'RuleOrder':12,
        'RuleName':"Finding Suppression - S3 general purpose buckets should have MFA delete "
        "enabled ",
        'Description':"This is not an explicit security requirement at this time.",
        'IsTerminal':False,
        'Criteria':
        {
            'Title': [
                {
                'Value': '2.1.3 Ensure MFA Delete is enabled on S3 buckets',
                'Comparison': 'EQUALS'
                },
                {
                'Value': 'S3.20 Ensure MFA Delete is enabled on S3 buckets',
                'Comparison': 'EQUALS'
                }
            ]
        },
        'Actions': [
        {
            'Type': 'FINDING_FIELDS_UPDATE',
            'FindingFieldsUpdate':{
                'Workflow': {
                    'Status': 'SUPPRESSED'
                }
            }
        }
        ],
    }
]

def get_existing_rules(session):
    """
    Retrieves existing automation rules from SecurityHub. Used to prevent duplicates.
    """
    securityhub = session.client('securityhub')
    existing_rules = []

    try:
        response = securityhub.list_automation_rules()
        existing_rules = response['AutomationRulesMetadata']

    except ClientError as client_error:
        error_message = client_error.response['Error']['Message']
        print(f"Failed to list automation rules. Error Message: {error_message}")

    return existing_rules

def enable_existing_rule(securityhub, rule):
    """
    Enables an existing automation rule in AWS Security Hub if it is not already enabled.

    Parameters:
    securityhub (boto3.client): The Security Hub client instance used to interact
    with AWS Security Hub.
    rule (dict): A dictionary containing details of the rule, including
    the 'RuleArn' and 'RuleName'.

    Returns:
    None

    This function will attempt to enable the rule and will print a message indicating whether
    the operation was successful. If an error occurs during the update, it will print
    an error message.
    """
    try:
        securityhub.batch_update_automation_rules(
            UpdateAutomationRulesRequestItems=[
                {
                    'RuleArn': rule["RuleArn"],
                    'RuleStatus': 'ENABLED'
                }
            ]
        )
        print(f"Rule {rule['RuleName']} was not enabled. Successfully updated to ENABLED.")
    except ClientError as client_error:
        print(f"Failed to update rule {rule['RuleName']}. "
              f"Error Message: {client_error.response['Error']['Message']}")

def create_new_rule(securityhub, rule):
    """
    Creates a new automation rule in AWS Security Hub.

    Parameters:
    securityhub (boto3.client): The Security Hub client instance used to interact with 
    AWS Security Hub.
    rule (dict): A dictionary containing the configuration for the new rule. This includes keys for 
                 'RuleStatus', 'RuleOrder', 'RuleName', 'Description', 'IsTerminal', 'Criteria', 
                 and 'Actions'.

    Returns:
    None

    This function attempts to create a new automation rule based on the provided configuration.
    It prints a message with the created rule's ARN if successful or an error message
    if the operation fails.
    """
    try:
        response = securityhub.create_automation_rule(
            RuleStatus=rule['RuleStatus'],
            RuleOrder=rule['RuleOrder'],
            RuleName=rule['RuleName'],
            Description=rule['Description'],
            IsTerminal=rule['IsTerminal'],
            Criteria=rule['Criteria'],
            Actions=rule['Actions']
        )
        print(f"Created Rule {rule['RuleOrder']}: {response['RuleArn']}.")
    except ClientError as client_error:
        print(f"Error creating rule {rule['RuleName']}: "
              f"{client_error.response['Error']['Message']}")

def create_automation_rules(session):
    """
    Creates or updates automation rules in AWS Security Hub.

    This function iterates through a predefined list of rules. For each rule, it checks if the
    rule already exists in Security Hub. If it does and is enabled, it skips the creation process.
    If the rule does not exist, it calls `create_new_rule` to create the rule.

    Parameters:
    session (boto3.Session): The session object to interact with AWS services.

    Returns:
    None
    """
    securityhub = session.client('securityhub')
    existing_rules = get_existing_rules(session)
    existing_rule_names = {rule['RuleName'] for rule in existing_rules}

    for rule in rules:
        if rule['RuleName'] in existing_rule_names:
            print(f"Rule with the name {rule['RuleName']} already "
                  "exists and is enabled. Skipping...")
        else:
            create_new_rule(securityhub, rule)

def main():
    """
    Main function for taking arguments, building the session,
    and running the script.
    """

    parser = argparse.ArgumentParser(description="Create automation rules for SecurityHub")
    parser.add_argument("-p","--profile", help="AWS SSO profile name", required=True)
    parser.add_argument("-r","--region", help="AWS region", default='us-west-2')
    args = parser.parse_args()

    session = boto3.Session(profile_name=args.profile, region_name=args.region)

    create_automation_rules(session)

if __name__ == '__main__':
    main()
