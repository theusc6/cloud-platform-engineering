# Executing the Terraform Deployment Prep Script

## Overview
This script deploys all resources necessary for management by CI/CD Github Actions pipeline.

## Actions
This script takes the following actions:
- Creates the state-locking DynamoDB table
- Creates a fully compliant S3 Bucket
- Creates the IAM role that will be assumed by Github Actions in DevOps account

## Usage
The script can be ran with the following command:

```
python3 terraform_deployment_prep.py --profile <insert profile here> --account_id <insert account id> --region <insert correct region> --project_name <insert project name>
```

## Target(s)
This script should be ran in any AWS account that requires resource deployment in preparation for CI/CD management.

## Considerations
N/A