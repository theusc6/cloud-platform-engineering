#!/usr/bin/env python3

"""
[ECS.5] ECS containers should be limited to read-only access to root filesystems
"""

import argparse
import boto3
from botocore.exceptions import ClientError

def main(profile, cluster_name):
    """
    Limit ECS containers to read-only access to root filesystems
    """
    session = boto3.Session(profile_name=profile)
    ecs = session.client('ecs')

    # Get the task definition and service ARNs
    try:
        response = ecs.list_services(cluster=cluster_name)
    except ClientError as error:
        print(f"Error listing services in cluster {cluster_name}: {error}")
        return

    service_arns = response['serviceArns']

    for service_arn in service_arns:
        try:
            response = ecs.describe_services(
                cluster=cluster_name,
                services=[service_arn]
            )
        except ClientError as error:
            print(f"Error describing service {service_arn}: {error}")
            continue

        if not response['services']:
            print(f"No services found for ARN {service_arn}")
            continue

        service = response['services'][0]
        task_definition_arn = service['taskDefinition']

        # Get the task definition family and container definitions
        try:
            response = ecs.describe_task_definition(
                taskDefinition=task_definition_arn
            )
        except ClientError as error:
            print(f"Error describing task definition {task_definition_arn}: {error}")
            continue

        task_definition = response['taskDefinition']
        family = task_definition['family']
        container_definitions = task_definition['containerDefinitions']

        # Modify container definitions to use read-only root filesystem and existing memory settings
        for container_definition in container_definitions:
            container_definition['readonlyRootFilesystem'] = True
            container_definition['memory'] = container_definition.get('memory', '512')
            container_definition['memoryReservation'] = container_definition.get(
                'memoryReservation',
                '512'
            )

        # Register the modified task definition
        try:
            response = ecs.register_task_definition(
                family=family,
                containerDefinitions=container_definitions,
                executionRoleArn=task_definition.get('executionRoleArn')
            )
        except ClientError as error:
            print(f"Error registering task definition {family}: {error}")
            continue

        new_task_definition_arn = response['taskDefinition']['taskDefinitionArn']

        # Update the service to use the new task definition
        try:
            response = ecs.update_service(
                cluster=cluster_name,
                service=service_arn,
                taskDefinition=new_task_definition_arn
            )
        except ClientError as error:
            print(f"Error updating service {service_arn}: {error}")
            continue

        print(f"Successfully updated service {service_arn} "
              f"to use read-only root filesystems and existing memory settings."
        )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Change ECS to read-only access to root filesystems.')
    parser.add_argument('-p', '--profile', required=True, help='Name of the AWS account profile')
    parser.add_argument('-c', '--cluster', required=True, help='Name of the ECS cluster')
    args = parser.parse_args()

    main(args.profile, args.cluster)
