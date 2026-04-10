# AWS Resource Tagging Script

This script allows for the addition of standard tags to various AWS resources. By leveraging the Boto3 library, the script streamlines the process of applying common tags to resources across different AWS services.

## Overview

This script aims to simplify the task of adding standardized tags to AWS resources. It is designed to be flexible, supporting a variety of AWS services such as S3, VPC, security groups, EC2 instances, ECS clusters, Lambda functions, and more. The script makes it easier to ensure consistent tagging practices across different services.

## How to Use

1. Replace the `AWS profile to use` placeholder with the appropriate AWS profile name in the script.

2. Run the script using a Python interpreter, ensuring you have the required dependencies installed.

3. Specify the target AWS service using the `-s` or `--service` argument followed by the service abbreviation (e.g., `s3`, `ec2`).

## Script Execution

The script performs the following actions:

1. Parses command-line arguments to obtain the AWS profile name and target service.

2. Checks if the provided service is supported by the script and exists in the specified AWS profile.

3. Retrieves a list of resources for the selected service using the `get_resources_by_service` function.

4. For each resource, adds predefined tags using the `add_tags_to_resource` function.

5. Prints messages indicating the addition of tags to resources or reports any errors encountered during the process.

## Note

- Ensure you have AWS CLI and Boto3 installed and configured before using this script.
- Supported services include S3 (`s3`), VPC (`vpc`), security groups (`securitygroup`), EC2 instances (`ec2`), ECS clusters (`ecs`), and Lambda functions (`lambda`).
- You can customize the tags added to resources by modifying the `tags` list in the `add_tags_to_resource` function.
- This script promotes consistent tagging practices, ensuring that essential tags are applied uniformly across different AWS resources.
