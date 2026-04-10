'''
This script enables Enhanced Monitoring for a specified RDS database instance and
creates the necessary IAM role and policy for it.

Enabling Enhanced Monitoring provides detailed real-time metrics for the RDS instance,
which is crucial for performance tuning and operational health monitoring of the database.
'''
import argparse
import json
import time
import boto3
from botocore.exceptions import ClientError

POLICY_NAME = "policy-myorg-rds-enhanced-monitoring+prod-ops"
ROLE_NAME = "role-myorg-rds-enhanced-monitoring+prod-ops"
LOG_GROUP_NAME = "/aws/rds/instance/enhanced-monitoring"

def get_policy_arn(iam_client, policy_name):
    """
    Retrieves the ARN of an existing policy by its name.
    """
    try:
        paginator = iam_client.get_paginator('list_policies')
        for response in paginator.paginate(Scope='Local'):
            for policy in response['Policies']:
                if policy['PolicyName'] == policy_name:
                    return policy['Arn']
    except ClientError as error:
        print(f"Error retrieving policy ARN: {error}")
    return None

def create_policy(iam_client, policy_name, policy_document):
    """
    Checks if the policy exists, if so, returns its ARN. If not, creates the policy.
    """
    policy_arn = get_policy_arn(iam_client, policy_name)
    if policy_arn:
        print(f"Policy {policy_name} already exists. ARN: {policy_arn}")
        return policy_arn

    try:
        response = iam_client.create_policy(
            PolicyName=policy_name,
            PolicyDocument=policy_document
        )
        print(f"Policy {policy_name} successfully created.")
        return response['Policy']['Arn']
    except ClientError as error:
        print(f"Error creating policy: {error}")
        return None

def get_role_arn(iam_client, role_name):
    """
    Retrieves the ARN of an existing role by its name.
    """
    try:
        response = iam_client.get_role(RoleName=role_name)
        return response['Role']['Arn']
    except ClientError as error:
        print(f"Error retrieving role ARN: {error}")
    return None

def create_role(iam_client, role_name, assume_role_policy_document):
    """
    Checks if the role exists, if so, returns its ARN. If not, creates the role.
    """
    role_arn = get_role_arn(iam_client, role_name)
    if role_arn:
        print(f"Role {role_name} already exists. ARN: {role_arn}")
        return role_arn

    try:
        response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=assume_role_policy_document
        )
        time.sleep(30)  # Wait a bit for the role to be fully created
        print(f"Role {role_name} successfully created.")
        return response['Role']['Arn']
    except ClientError as error:
        print(f"Error creating role: {error}")
        return None

def attach_policy_to_role(iam_client, role_name, policy_arn):
    """
    Attached the above policy and role
    """
    try:
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_arn
        )
        time.sleep(30)
        print(f"Policy {policy_arn} attached to role {role_name}.")
    except ClientError as error:
        print(f"Error attaching policy to role: {error}")

def enable_enhanced_monitoring(rds_client, db_instance_identifier, monitoring_interval,
                               role_arn):
    """
    Enables enhanced monitoring on the target DB
    """
    try:
        rds_client.modify_db_instance(
            DBInstanceIdentifier=db_instance_identifier,
            MonitoringInterval=monitoring_interval,
            MonitoringRoleArn=role_arn,
            ApplyImmediately=True
        )
        print(f"Enabled Enhanced Monitoring for RDS instance: {db_instance_identifier}")
    except ClientError as error:
        print(f"Error enabling Enhanced Monitoring: {error.response['Error']['Message']}")

def create_log_group(cw_client, log_group_name):
    """
    Creates a CloudWatch log group.
    """
    try:
        cw_client.create_log_group(logGroupName=log_group_name)
        print(f"Created log group: {log_group_name}")
        return log_group_name
    except ClientError as error:
        if error.response['Error']['Code'] == 'ResourceAlreadyExistsException':
            print(f"Log group {log_group_name} already exists.")
        else:
            print(f"Error creating log group: {error}")
        return log_group_name

def create_log_stream(cw_client, log_group_name, log_stream_name):
    """
    Creates a CloudWatch log stream within a log group. If the log stream already exists,
    it simply returns the name of the existing log stream.
    """
    try:
        cw_client.create_log_stream(
            logGroupName=log_group_name,
            logStreamName=log_stream_name
        )
        print(f"Created log stream: {log_stream_name} in log group: {log_group_name}")
    except ClientError as error:
        if error.response['Error']['Code'] == 'ResourceAlreadyExistsException':
            print(f"Log stream {log_stream_name} already exists in log group {log_group_name}.")
        else:
            print(f"Error creating log stream: {error}")
            return None
    return log_stream_name

def main():
    """
    Main Function
    """
    parser = argparse.ArgumentParser(description="Enable Enhanced Monitoring for RDS Database")
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('-d', '--dbinstance', required=True, type=str,
                        help='Identifier of the RDS database instance')
    parser.add_argument('-i', '--interval', required=True, type=int,
                        help='Monitoring interval in seconds')
    parser.add_argument('-r', '--region', required=False, default="us-west-2", type=str,
                        help='AWS region where the RDS instance is located')

    args = parser.parse_args()

    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    iam_client = session.client('iam')
    rds_client = session.client('rds')

    log_stream_name = f"enhanced-monitoring-stream-{args.dbinstance}"

    # Create CloudWatch client
    cw_client = session.client('logs')

    # Create CloudWatch Log Group and Stream
    create_log_group(cw_client, LOG_GROUP_NAME)
    create_log_stream(cw_client, LOG_GROUP_NAME, log_stream_name)

    policy_document = json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "EnableCreationAndManagementOfRDSCloudwatchLogGroups",
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:PutRetentionPolicy"
                ],
                "Resource": [
                    "arn:aws:logs:*:*:log-group:RDS*"
                ]
            },
            {
                "Sid": "EnableCreationAndManagementOfRDSCloudwatchLogStreams",
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "logs:DescribeLogStreams",
                    "logs:GetLogEvents"
                ],
                "Resource": [
                    "arn:aws:logs:*:*:log-group:RDS*:log-stream:*"
                ]
            }
        ]
    })
    assume_role_policy_document = json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "monitoring.rds.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    })

    policy_arn = create_policy(iam_client, POLICY_NAME, policy_document)
    if policy_arn:
        role_arn = create_role(iam_client, ROLE_NAME, assume_role_policy_document)
        if role_arn:
            attach_policy_to_role(iam_client, ROLE_NAME, policy_arn)
            enable_enhanced_monitoring(rds_client, args.dbinstance, args.interval,
                                       role_arn)

if __name__ == "__main__":
    main()
