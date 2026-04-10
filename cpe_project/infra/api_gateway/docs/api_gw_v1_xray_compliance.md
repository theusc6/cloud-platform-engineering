# AWS API Gateway X-Ray Tracing Compliance Script

This script enables X-Ray tracing for AWS API Gateway Stages. It offers the flexibility to enable X-Ray tracing for all stages of a specified Rest API or to process all Rest APIs in the AWS account and enable X-Ray tracing for their stages. The script utilizes the AWS SDK for Python (Boto3) to interact with the AWS API Gateway service.

## Usage

```bash
python api_gw_xray_compliance.py -p my_profile -r us-west-2 --api my_api_id
```

- To enable X-Ray tracing for all stages of a specific Rest API, use the `--api` option followed by the Rest API ID.

```bash
python api_gw_xray_compliance.py -p my_profile -r us-west-2 --all
```

- To enable X-Ray tracing for all Rest APIs in the account, use the `--all` option.

## Command-line Arguments

The script accepts the following command-line arguments:

- `-p` or `--profile`: (Required) Specifies the AWS profile name for Single Sign-On (SSO) login.

- `-r` or `--region`: (Optional) Specifies the AWS region. The default region is 'us-west-2'.

- `--api`: (Optional) Specifies the ID of a specific Rest API to enable X-Ray tracing for all its stages.

- `--all`: (Optional) If this flag is present, the script processes all Rest APIs in the AWS account and enables X-Ray tracing for their stages.

## Functionality

The script provides two main functions to enable X-Ray tracing:

1. `enable_xray_tracing`: Enables X-Ray tracing for a given API Gateway Stage.

2. `process_all_stages_of_api`: Loops through all the Stages of a specific Rest API and enables X-Ray tracing for each stage.

3. `process_all_rest_apis`: Loops through all the API Gateway APIs and their Stages, enabling X-Ray tracing for each stage.

## Prerequisites

1. Python 3.x with `argparse` and `boto3` libraries installed.

2. Proper AWS credentials set up, including an AWS profile with appropriate permissions for interacting with the API Gateway service.

## Example

To enable X-Ray tracing for all stages of a specific Rest API:

```bash
python api_gw_xray_compliance.py -p my_profile -r us-west-2 --api my_api_id
```

To enable X-Ray tracing for all Rest APIs in the account:

```bash
python api_gw_xray_compliance.py -p my_profile -r us-west-2 --all
```

## Usage in Compliance Workflow

This script is intended to be used as part of a larger process to ensure AWS API Gateway security compliance. By enabling X-Ray tracing for all API Gateway Stages, you gain insights into how requests are flowing through your APIs, which helps identify potential performance and security issues.

Please ensure you review and understand any script before running it to ensure it aligns with your specific requirements and intended outcome.
