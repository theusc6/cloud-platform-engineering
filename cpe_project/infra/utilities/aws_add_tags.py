#!/usr/bin/env python3
# using python3 and aws cli v2.9.13 or higher

"""
Add standard tags to AWS resources.
"""

import argparse
import botocore.exceptions
import boto3

def get_resources_by_service(service_name, aws_profile):
    """
    Define the resources to tag based on the service name.
    """
    session = boto3.Session(profile_name=aws_profile)
    resources = []

    if service_name == 's3':
        client = session.client('s3')
        resources = [bucket['Name'] for bucket in client.list_buckets()['Buckets']]
    elif service_name == 'vpc':
        client = session.client('ec2')
        resources = [vpc['VpcId'] for vpc in client.describe_vpcs()['Vpcs']]
    elif service_name == 'securitygroup':
        client = session.client('ec2')
        resources = [sg['GroupId'] for sg in client.describe_security_groups()['SecurityGroups']]
    elif service_name == 'ec2':
        client = session.client('ec2')
        resources = [
            instance['InstanceId']
            for instance in client.describe_instances()['Reservations'][0]['Instances']
        ]
    elif service_name == 'ecs':
        client = session.client('ecs')
        resources = [cluster['clusterArn'] for cluster in client.list_clusters()['clusterArns']]
    elif service_name == 'lambda':
        client = session.client('lambda')
        resources = [function['FunctionArn'] for function in client.list_functions()['Functions']]
    # Add more services here as needed

    return resources

def add_tags_to_resource(service_name, resource_name, aws_profile):
    """
    Add tags to the resource.
    """
    session = boto3.Session(profile_name=aws_profile)

    tags = [
        # Required tags as of 2023-04-26 which will change based on AWS Account
        {'Key': 'Category', 'Value': 'LabTech'},
        {'Key': 'Product', 'Value': 'Redacted'}
    ]

    try:
        if service_name == 's3':
            client = session.client('s3')
            client.put_bucket_tagging(Bucket=resource_name, Tagging={'TagSet': tags})
        elif service_name in ['vpc', 'securitygroup', 'ec2']:
            client = session.client('ec2')
            client.create_tags(Resources=[resource_name], Tags=tags)
        elif service_name == 'ecs':
            client = session.client('ecs')
            client.tag_resource(resourceArn=resource_name, tags=tags)
        elif service_name == 'lambda':
            client = session.client('lambda')
            client.tag_resource(Resource=resource_name,
                                Tags={tag['Key']: tag['Value'] for tag in tags})
        else:
            print(f"Unsupported service: {service_name}")
            return
        print(f"Added tags to {service_name} resource: {resource_name}")
    except botocore.exceptions.BotoCoreError as error:
        print(f"Failed to add tags to {service_name} resource: {resource_name}. Error: {error}")

def service_exists(service_name, aws_profile):
    """
    Check that the service exists.
    """
    try:
        session = boto3.Session(profile_name=aws_profile)
        available_services = session.get_available_services()
        return bool(service_name in available_services)
    except botocore.exceptions.BotoCoreError as error:
        print(f"Error while checking service existence: {error}")
        return False

def main():
    """
    Main function.
    """
    parser = argparse.ArgumentParser(description='Add tags to AWS resources.')
    parser.add_argument('-p', '--profile', required=True, help='AWS profile to use.')
    parser.add_argument('-s', '--service', required=True,
                        help='AWS service to tag resources (e.g., s3).')
    args = parser.parse_args()

    supported_services = ['s3', 'vpc', 'securitygroup', 'ec2', 'ecs', 'lambda']

    service_name = args.service.lower()

    if service_name in supported_services:
        checked_service_name = service_name if service_name != 'vpc' else 'ec2'
        if service_exists(checked_service_name, args.profile):
            resources = get_resources_by_service(service_name, args.profile)
            if resources:
                for resource_name in resources:
                    add_tags_to_resource(service_name, resource_name, args.profile)
            else:
                print(f"No resources found for {service_name} in the provided AWS profile.")
        else:
            print(f"The service '{service_name}' does not exist in the provided AWS profile "
                  f"or is not supported by this script."
            )
    else:
        print(f"The service '{service_name}' is not supported by this script. Supported services: "
              f"{', '.join(supported_services)}"
        )

if __name__ == '__main__':
    main()
