"""
This module queries AWS IAM for roles and policies containing a
specified keyword in their name and outputs the results to an 
Excel spreadsheet. The script uses Boto3 to interface with AWS 
IAM and Pandas along with OpenPyXL to create and format the output
spreadsheet.

The Excel spreadsheet will include details such as role names,
policy names, policy types, permissions, and the last time each 
role was used. For inline policies, it fetches the specific  policy
document. For managed policies, it fetches the permissions from
the policy's default version.
"""
import argparse
import boto3
import pandas as pd
from openpyxl.styles import Alignment
from botocore.exceptions import ClientError

ROLE_NAME_KEY = 'Role Name'


def parse_args():
    """
    Parse command-line arguments passed to the script.
    """
    parser = argparse.ArgumentParser(
        description='Query for IAM roles and policies with a specified keyword in their name.'
    )
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name')
    parser.add_argument('-k', '--keyword', required=True, type=str,
                        help='Keyword to search in IAM roles and policies')
    return parser.parse_args()

def list_roles_policies_with_keyword(client, keyword):
    """
    List all IAM roles and policies that include the specified keyword in their name.
    """
    keyword_lower = keyword.lower()
    filtered_roles = []
    filtered_policies = []

    # Paginator for roles
    try:
        paginator = client.get_paginator('list_roles')
        for page in paginator.paginate():
            roles = page['Roles']
            filtered_roles.extend([
                role for role in roles if keyword_lower in role['RoleName'].lower()
            ])
    except ClientError as error:
        print(f"Error listing roles: {error}")
        return [], []

    # Paginator for policies
    try:
        paginator = client.get_paginator('list_policies')
        for page in paginator.paginate(Scope='Local'):
            policies = page['Policies']
            filtered_policies.extend([
                policy for policy in policies if keyword_lower in policy['PolicyName'].lower()
            ])
    except ClientError as error:
        print(f"Error listing policies: {error}")
        return filtered_roles, []

    return filtered_roles, filtered_policies

def get_policy_permissions(client, policy_arn):
    """
    Get detailed information about the policy.
    """
    try:
        policy_version = client.get_policy(PolicyArn=policy_arn)['Policy']['DefaultVersionId']
        policy_document = client.get_policy_version(PolicyArn=policy_arn, VersionId=policy_version)
        policy_statements = policy_document['PolicyVersion']['Document']['Statement']

        permissions = []
        for statement in policy_statements:
            # Each statement can have single or multiple actions and resources
            actions = statement.get('Action', [])
            if not isinstance(actions, list):
                actions = [actions]  # Convert to list if single action

            resources = statement.get('Resource', [])
            if not isinstance(resources, list):
                resources = [resources]  # Convert to list if single resource

            effect = statement.get('Effect', 'N/A')

            for action in actions:
                for resource in resources:
                    permissions.append(f"Effect: '{effect}' - Action: '{action}' - "
                                       f"Resoure(s): '{resource}'")

        return '; '.join(permissions)

    except ClientError as error:
        print(f"An error occurred: {error}")
        return 'Error retrieving permissions'

def get_role_policies(client, role_name):
    """
    Get all policies (both managed and inline) attached to a role.
    """
    policies = []

    # Get managed attached policies
    try:
        managed_policies = client.list_attached_role_policies(
            RoleName=role_name)['AttachedPolicies']
        for policy in managed_policies:
            # Check if the policy is AWS managed or customer managed by examining the ARN
            if ':aws:policy/' in policy['PolicyArn']:
                policy_type = 'AWS Managed'
            else:
                policy_type = 'Customer Managed'

            policies.append({
                'PolicyName': policy['PolicyName'],
                'PolicyType': policy_type,
                'PolicyArn': policy['PolicyArn']  # Include ARN for managed policies
            })
    except ClientError as error:
        print(f"Error retrieving managed policies for role {role_name}: {error}")

    # Get inline policies
    try:
        inline_policies = client.list_role_policies(RoleName=role_name)['PolicyNames']
        for policy_name in inline_policies:
            policies.append({
                'PolicyName': policy_name,
                'PolicyType': 'Inline'
                # Inline policies do not have ARNs
            })
    except ClientError as error:
        print(f"Error retrieving inline policies for role {role_name}: {error}")

    return policies

def get_inline_policy_document(client, role_name, policy_name):
    """
    Get the policy document for an inline policy attached to a role.
    """
    try:
        policy_document_response = client.get_role_policy(
        RoleName=role_name,
        PolicyName=policy_name
    )
        policy_document = policy_document_response['PolicyDocument']
        return policy_document
    except ClientError as error:
        print(f"Error retrieving policy document for inline policy {policy_name}: {error}")
        return None

def format_policy_document(policy_document):
    """
    Break down the policy document into a list of dictionaries with
    Effect, Action, and Resource keys.
    """
    permissions = []
    for statement in policy_document.get('Statement', []):
        actions = statement.get('Action', [])
        if not isinstance(actions, list):
            actions = [actions]

        resources = statement.get('Resource', [])
        if not isinstance(resources, list):
            resources = [resources]

        effect = statement.get('Effect', 'N/A')

        for action in actions:
            for resource in resources:
                permissions.append({
                    'Effect': effect,
                    'Action': action,
                    'Resource': resource
                })
    return permissions

def get_role_last_used(client, role_name):
    """
    Get the last used timestamp of the IAM role.
    """
    try:
        role_details = client.get_role(RoleName=role_name)
        last_used = role_details['Role'].get('RoleLastUsed', {}).get('LastUsedDate')

        if last_used:
    # Convert to timezone-naive datetime if not None
            return last_used.replace(tzinfo=None)
        return 'Never Used'
    except ClientError as error:
        print(f"Error retrieving last used details for role {role_name}: {error}")
        return 'Error retrieving information'

def process_role_policies(role, iam_client):
    """
    Processes all policies attached to a specified IAM role and generates a
    list of data for each policy.
    """
    role_name = role['RoleName']
    role_policies = get_role_policies(iam_client, role_name)
    role_last_used = get_role_last_used(iam_client, role_name)
    return [
            create_policy_data(policy, role_name, iam_client, role_last_used)
            for policy in role_policies
        ]

def create_policy_data(policy, role_name, iam_client, role_last_used):
    """
    Creates and returns a dictionary of policy data for a given IAM role.
    """
    policy_name = policy['PolicyName']
    policy_type = policy['PolicyType']
    permissions = process_policy_type(policy, role_name, iam_client, policy_type)
    return {
        ROLE_NAME_KEY: role_name,
        'Policy Name': policy_name,
        'Policy Type': policy_type,
        'Permissions': permissions,
        'Last Used': role_last_used
    }

def process_policy_type(policy, role_name, iam_client, policy_type):
    """
    Processes a given policy based on its type (Inline or Managed) and retrieves its permissions.
    """
    if policy_type == 'Inline':
        policy_document = get_inline_policy_document(iam_client, role_name, policy['PolicyName'])
        if policy_document:
            return format_policy_document(policy_document)
        return 'Error retrieving policy document'
    return get_policy_permissions(iam_client, policy['PolicyArn'])

def main():
    """
    Main function.
    """
    args = parse_args()
    session = boto3.Session(profile_name=args.profile)
    iam_client = session.client('iam')

    filtered_roles, _ = list_roles_policies_with_keyword(iam_client, args.keyword)
    data_for_excel = [
            policy_data
            for role in filtered_roles
            for policy_data in process_role_policies(role, iam_client)
        ]
    if not data_for_excel:
        print("No data was collected. Exiting without writing to Excel.")
        return

    create_excel(data_for_excel)    # Data accumulation for Excel output

def create_excel(data_for_excel):
    """
    Creates an Excel file with data from IAM role and policy queries.
    """
    data_frame = pd.DataFrame(data_for_excel)

    writer = pd.ExcelWriter('iam_roles_policies.xlsx', engine='openpyxl') # pylint: disable=abstract-class-instantiated
    data_frame.to_excel(writer, index=False, sheet_name='Permissions')

    worksheet = writer.sheets['Permissions']

    # Apply a filter to all columns
    worksheet.auto_filter.ref = worksheet.dimensions

    # Freeze the first row with headers
    worksheet.freeze_panes = 'A2'

    # Set the width of the permissions column and enable text wrapping
    permissions_column = worksheet.column_dimensions['D']
    permissions_column.width = 100
    for cell in worksheet['D']:
        cell.alignment = Alignment(wrap_text=True)

    # Group rows by role name and merge
    unique_roles = data_frame[ROLE_NAME_KEY].unique()
    for role in unique_roles:
        role_rows = data_frame[data_frame[ROLE_NAME_KEY] == role].index.tolist()
        first_row = role_rows[0] + 2
        last_row = role_rows[-1] + 2
        if len(role_rows) > 1:
            worksheet.merge_cells(
                start_row=first_row,
                start_column=1,
                end_row=last_row,
                end_column=1
            )

    writer.close()

if __name__ == "__main__":
    main()
