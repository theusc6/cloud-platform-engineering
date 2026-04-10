"""
This script enables logging on a specific AWS Step Functions state machine.

Usage: python3 enable_logging.py -p <profile_name> -n <state_machine_name> -l <log_level>
"""

import argparse
import json
import boto3
from botocore.exceptions import ClientError


def parse_args():
    """
    Parse command-line arguments passed to the script.
    """
    parser = argparse.ArgumentParser(
        description='Enable logging on an AWS Step Functions state machine.'
    )
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('-n', '--name', required=True, type=str,
                        help='State Machine name')
    parser.add_argument('-l', '--level', required=True, type=str,
                        help='Log level: ERROR, FATAL, OFF, ALL')
    parser.add_argument('-r', '--region', type=str,
                        help='AWS region for the state machine')
    return parser.parse_args()

def get_or_create_cloudwatch_log_role(session):
    """
    Get or create CloudWatch Logs role.
    """
    role_name = 'StepFunctionsCloudWatchLogsRole'
    policy_arns = [
        'arn:aws:iam::aws:policy/CloudWatchLogsFullAccess',
        'arn:aws:iam::aws:policy/AWSStepFunctionsFullAccess'
    ]
    assume_role_policy_document = {
        'Version': '2012-10-17',
        'Statement': [{
            'Effect': 'Allow',
            'Principal': {'Service': 'states.amazonaws.com'},
            'Action': 'sts:AssumeRole'
        }]
    }

    iam = session.client('iam')

    # Check if the role exists
    try:
        role = iam.get_role(RoleName=role_name)
        print(f"Role '{role_name}' already exists.")
        cloudwatch_logs_role_arn = role['Role']['Arn']
    except ClientError as get_role_error:
        if get_role_error.response['Error']['Code'] == 'NoSuchEntity':
            try:
                iam.create_role(
                    RoleName=role_name,
                    AssumeRolePolicyDocument=json.dumps(assume_role_policy_document)
                )
                print(f"{role_name} successfully created")
                cloudwatch_logs_role_arn = iam.get_role(RoleName=role_name)['Role']['Arn']
            except ClientError as create_role_error:
                print(f"An error occurred: {create_role_error.response['Error']['Message']}")
                return None
        else:
            print(f"An error occurred: {get_role_error.response['Error']['Message']}")
            return None

    # Validate if the policy is attached
    for policy_arn in policy_arns:
        try:
            attached_policies_response = iam.list_attached_role_policies(
                RoleName=role_name
            )
            attached_policies = [
                policy['PolicyArn'] for policy in attached_policies_response['AttachedPolicies']
            ]

            if policy_arn not in attached_policies:
                print(f"Policy '{policy_arn}' is not attached to role '{role_name}'. "
                    "Attaching now...")
                iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
                print(f"Attached policy '{policy_arn}' to role '{role_name}'")
            else:
                print(f"Policy '{policy_arn}' is already attached to role '{role_name}'")
        except ClientError as list_policies_error:
            print(f"An error occurred: {list_policies_error.response['Error']['Message']}")
            return None

    cloudwatch_logs_role_arn = iam.get_role(RoleName=role_name)['Role']['Arn']
    return cloudwatch_logs_role_arn

def create_log_group(logs_client, log_group_name):
    """
    Create a CloudWatch Logs log group and return its ARN.
    """
    try:
        logs_client.create_log_group(logGroupName=log_group_name)
    except logs_client.exceptions.ResourceAlreadyExistsException:
        print(f"Log group {log_group_name} already exists.")

    response = logs_client.describe_log_groups(logGroupNamePrefix=log_group_name)
    return response['logGroups'][0]['arn']

class StateMachineNotFound(Exception):
    """
    Exception raised when a specified Step Functions state machine is not found.
    """

def get_state_machine_arn(sfn_client, name):
    """
    Get the ARN of the specified Step Functions state machine by its name.
    """
    try:
        response = sfn_client.list_state_machines()
        for state_machine in response['stateMachines']:
            if state_machine['name'] == name:
                return state_machine['stateMachineArn']
    except ClientError as client_error:
        error_message = client_error.response['Error']['Message']
        error_code = client_error.response['Error']['Code']

        if error_code == "StateMachineDoesNotExist":
            print(f"Error: State machine with name '{name}' not found. "
                f"Please ensure the state machine name is correct and try again."
                f"Error Message: {error_message}.")
            return None

    print(f"State machine with name '{name}' not found.")
    return None

def enable_logging(sfn_client, logs_client, state_machine_arn, log_level, cloudwatch_logs_role_arn):
    """
    Enable logging on the specified Step Functions state machine.
    """
    # Create a new log group (you can customize the name as needed)
    log_group_name = f"/aws/stepfunctions/{state_machine_arn.split(':')[-1]}"
    log_group_arn = create_log_group(logs_client, log_group_name)

    try:
        sfn_client.update_state_machine(
            roleArn=cloudwatch_logs_role_arn,
            loggingConfiguration={
                'level': log_level,
                'includeExecutionData': True,
                'destinations': [
                    {
                        'cloudWatchLogsLogGroup': {
                            'logGroupArn': log_group_arn
                        }
                    }
                ]
            },
            stateMachineArn=state_machine_arn
        )
        print(f"Success! Enabled logging on state machine '{state_machine_arn}' "
              f"with level '{log_level}'.")
    except ClientError as client_error:
        error_message = client_error.response['Error']['Message']
        print(f"An error occurred: {error_message}")

def main():
    """
    Main function of the script.
    """
    args = parse_args()
    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    sfn_client = session.client('stepfunctions')
    logs_client = session.client('logs')

    # Get or create CloudWatch Logs role
    cloudwatch_logs_role_arn = get_or_create_cloudwatch_log_role(session)

    state_machine_arn = get_state_machine_arn(sfn_client, args.name)
    if state_machine_arn is not None:
        enable_logging(sfn_client, logs_client, state_machine_arn,
                       args.level, cloudwatch_logs_role_arn)
    else:
        return
if __name__ == "__main__":
    main()
