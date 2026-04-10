# AWS API Gateway Execution Logging and X-Ray Tracing Configuration

This script is used to configure Execution Logging and X-Ray Tracing for AWS API Gateway Stages (REST API).

## Purpose

The purpose of this script is to enable and configure execution logging and X-Ray tracing for API Gateway stages. It provides the ability to configure a single specified API or all APIs within an AWS account.

## Prerequisites

Before using the script, ensure the following:

1. Python 3 is installed on the system.
2. AWS CLI is installed and configured with appropriate IAM permissions.
3. The script requires the `boto3` library to interact with AWS services. To install `boto3`, run `pip install boto3` in the terminal.

## Usage

To run the script, use the following commands in the terminal:

```bash
python3 api_gw_v1_execution_logging.py --profile <profile_name> -r <region> --api <api_id>
python3 api_gw_v1_execution_logging.py --profile <profile_name> -r <region> --all
```

Where:

- `<profile_name>`: The AWS CLI profile name to use for SSO login. This is a required parameter.
- `<region>`: The AWS region to work in. This is an optional parameter with a default value of `us-west-2`.
- `<api_id>`: The ID of the specific REST API to configure. Use this when you want to enable execution logging and X-Ray tracing for a single API. This is an optional parameter when using the `--all` option.

## Functionality

### 1. Parsing Command-line Arguments

The script uses the `argparse` library to parse command-line arguments. The following options are available:

- `-p` or `--profile`: Specifies the AWS CLI profile name for Single Sign-On (SSO) login. This is a required argument.
- `-r` or `--region`: Specifies the AWS region to work in. If not provided, the default region is `us-west-2`.
- `-api` or `--api`: Specifies the ID of a specific REST API to configure. This is an optional argument.
- `-a` or `--all`: If provided, the script will process all REST APIs in the AWS account. This is an optional argument.

### 2. Get or Create CloudWatch Logs Role

The function `get_or_create_cloudwatch_log_role(session)` checks if an existing CloudWatch Logs role is assigned to API Gateway. If not, it creates a new role and attaches the necessary policy to it. The CloudWatch Logs role is required for logging API Gateway execution data to CloudWatch Logs.

### 3. Enable Execution Logging and X-Ray Tracing for a Stage

The function `enable_execution_logging_and_tracing_for_stage(apigw, rest_api_id, stage_name)` is responsible for enabling execution logging and X-Ray tracing for a specific stage of the API Gateway REST API. It uses the `update_stage` API to apply the necessary configurations.

### 4. Process All Stages of a Specific API

The function `process_all_stages_of_api(session, api_id)` processes all stages of a specific REST API. It retrieves the stages of the specified API using `get_stages` and then enables execution logging and X-Ray tracing for each stage.

### 5. Process All REST APIs

The function `process_all_rest_apis(session)` processes all REST APIs in the AWS account. It uses the `get_rest_apis` API to retrieve a list of all APIs and then calls the `process_all_stages_of_api` function for each API.

### 6. Main Function

The `main()` function is the entry point of the script. It first parses the command-line arguments using `parse_args()`. Then, it creates a Boto3 session with the specified AWS CLI profile and region. Next, it calls `get_or_create_cloudwatch_log_role(session)` to ensure the CloudWatch Logs role exists or is created. Finally, depending on the provided arguments (`--api` or `--all`), it processes either a specific API or all APIs in the AWS account.

## Notes

- The script relies on the `boto3` library to interact with AWS services, and the AWS CLI profile provided must have appropriate permissions to perform the required actions.
- Ensure you have the necessary IAM permissions to create roles, update API Gateway configurations, and attach policies.
- This script configures Execution Logging and X-Ray Tracing for API Gateway **Stages**. If you need to configure logging and tracing for the entire API (including all stages), you should modify the script accordingly.

Please ensure you review and understand any script before running it to ensure it aligns with your specific requirements and intended outcome.
