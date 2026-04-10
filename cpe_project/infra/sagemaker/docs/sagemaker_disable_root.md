# Disable Root Access for SageMaker Notebook Instance

This script is designed to disable root access for a specific Amazon SageMaker notebook instance. 

## Usage


`python3 disable_root_access.py -p <profile_name> -r <region_name> -i <notebook_instance_name>`

## Argument Parsing

The script expects three command-line arguments:

- `-p` or --profile: AWS profile name for SSO login.
- `-r` or --region: AWS region where the SageMaker notebook instance is located.
- `-i` or --instance: SageMaker notebook instance name.

Boto3 Session Creation: A session with AWS is created using the provided profile and region.

Disabling Root Access: The script then calls the update_notebook_instance method from the SageMaker client of Boto3 to disable root access.

Exception Handling: If any error occurs during the execution, it is caught and displayed to the user.

## Dependencies
- boto3
- botocore

Ensure that you have these libraries installed in your environment before executing the script.
