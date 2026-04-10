# AWS API Gateway v2 Access Logging Configuration Script

This script is used to configure access logging for AWS API Gateway v2 stages. It provides the capability to specify the AWS profile name for Single Sign-On (SSO) login, the AWS region (with a default of us-west-2), a specific HTTP API ID, or to process all HTTP APIs in the account.

## Usage

```bash
python3 api_gw_v2_configure_access_logging.py --profile <profile_name> --api <api_id>
```

- To enable access logging for all stages of a specific HTTP API, use the `--api` option followed by the HTTP API ID.

```bash
python3 api_gw_v2_configure_access_logging.py --profile <profile_name> --all
```

- To enable access logging for all stages of all HTTP APIs in the account, use the `--all` option.

## Command-line Arguments

The script accepts the following command-line arguments:

- `-p` or `--profile`: (Required) Specifies the AWS profile name for Single Sign-On (SSO) login.

- `-r` or `--region`: (Optional) Specifies the AWS region. The default region is 'us-west-2'.

- `-api` or `--api`: (Optional) Specifies the ID of a specific HTTP API to enable access logging for all its stages.

- `-a` or `--all`: (Optional) If this flag is present, the script processes all HTTP APIs in the AWS account and enables access logging for their stages.

## Functionality

The script provides two main functions:

1. `create_log_group`: Creates a new CloudWatch log group and tags it with 'Category: Security'.

2. `enable_access_logging`: Enables access logging for a given API Gateway v2 Stage by updating the stage with the specified log group.

## Prerequisites

1. Python 3.x with `argparse`, `re`, and `boto3` libraries installed.

2. Proper AWS credentials set up, including an AWS profile with appropriate permissions for interacting with the API Gateway v2 and CloudWatch services.

## Access Logging Format

The access log format is in JSON, containing the following fields:

- `requestId`: The unique request ID.
- `ip`: The source IP of the request.
- `caller`: The identity of the caller making the request.
- `user`: The user identity associated with the request.
- `requestTime`: The timestamp of the request.
- `httpMethod`: The HTTP method of the request.
- `resourcePath`: The resource path of the request.
- `status`: The HTTP status code of the response.
- `protocol`: The protocol of the request.
- `responseLength`: The length of the response.

## Example

To enable access logging for all stages of a specific HTTP API:

```bash
python3 api_gw_v2_configure_access_logging.py --profile my_profile --api my_api_id
```

To enable access logging for all stages of all HTTP APIs in the account:

```bash
python3 api_gw_v2_configure_access_logging.py --profile my_profile --all
```

## Usage in Compliance Workflow

This script can be used as part of a larger process to ensure AWS API Gateway v2 security compliance. By enabling access logging for all stages of API Gateway v2, you can monitor and audit API traffic, helping to identify potential security threats and unauthorized access attempts. The tagging of the log groups with 'Category: Security' helps in categorizing logs and organizing them based on security requirements.

Please ensure you review and understand any script before running it to ensure it aligns with your specific requirements and intended outcome.
