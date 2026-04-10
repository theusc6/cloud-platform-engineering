# ECS Containers Read-Only Root Filesystems

This script is designed to address [ECS.5](https://learn.cisecurity.org/benchmarks-ecs-v1-0-0-cs-5/) from the Center for Internet Security (CIS) Amazon Elastic Container Service (ECS) benchmark. The script ensures that ECS containers are limited to read-only access to root filesystems within the specified ECS cluster. By enforcing this security measure, you enhance the security posture of your ECS environment.

## Overview

The script is aimed at automating the process of modifying ECS task definitions and service configurations to restrict containers from writing to root filesystems. This is achieved by setting the `readonlyRootFilesystem` property to `True` for each container. The script also ensures that existing memory settings are retained for the containers.

## How to Use

1. Replace the placeholders in the script with appropriate values for your AWS environment.
   - `Profile`: The name of the AWS account profile to be used for authentication.
   - `Cluster`: The name of the ECS cluster where the changes will be applied.

2. Run the script using a Python interpreter with the required dependencies installed.

## Script Execution

The script performs the following actions:

1. Establishes an AWS session using the provided profile.

2. Retrieves the ARNs of services in the specified ECS cluster.

3. For each service, modifies the associated task definition to enforce read-only root filesystems.

4. Registers the modified task definition and updates the service to use it.

5. Prints success messages for each updated service.

## Note

- By adhering to CIS benchmarks, this script enhances the security of ECS containers by enforcing read-only access to root filesystems.
- The script is specifically designed to address ECS.5 from the CIS Amazon ECS benchmark.
- Ensure that the provided profile and cluster name are accurate and valid within your AWS environment.

---

Utilizing this script helps align your ECS environment with security best practices, minimizing the potential attack surface by preventing containers from writing to root filesystems. This automation reduces the manual effort required to maintain security configurations and ensures consistent adherence to CIS benchmarks within your AWS infrastructure.
