# CloudFormation Stack Query

## Overview
This script queries all CloudFormation stacks in specified AWS accounts and regions. It captures detailed information about each stack and its associated resources, then exports this data into an Excel file with each stack's data on a separate sheet for better readability.

## Actions
This script performs the following actions:
- Queries all CloudFormation stacks in the specified AWS account and region.
- For each CloudFormation stack, it collects the following details:
  - **Stack Name**
    - The name of the CloudFormation stack.
  - **Stack ID**
    - The unique identifier for the stack.
  - **Stack Status**
    - The current status of the stack (e.g., `CREATE_COMPLETE`, `UPDATE_IN_PROGRESS`).
  - **Creation Time**
    - The timestamp when the stack was created.
  - **Last Updated Time**
    - The timestamp when the stack was last updated.
  - **Region**
    - The AWS region where the stack is deployed.
  - **Tags**
    - Key-value pairs associated with the stack for identification and categorization.
  - **Capabilities**
    - Any capabilities required by the stack (e.g., `CAPABILITY_IAM`, `CAPABILITY_NAMED_IAM`).
  - **Resource Type**
    - The type of each resource in the stack (e.g., `AWS::EC2::Instance`).
  - **Logical Resource ID**
    - The logical identifier of the resource within the CloudFormation template.
  - **Physical Resource ID**
    - The actual resource ID in AWS (e.g., instance ID or bucket name).
  - **Resource Status**
    - The current status of each resource (e.g., `CREATE_COMPLETE`, `UPDATE_IN_PROGRESS`).

- The collected data is exported into an Excel document named `cloudformation_stacks_and_resources_<account_id>_<date>.xlsx`, with each CloudFormation stack’s data presented on a separate sheet.

## Usage
The script can be executed with the following command:

```
python3 cloudformation_stack_query.py --profile <profile_name> --regions <region1> <region2>
```

## Targets
This script should be ran against an account to report on the cloudformation stacks that have been deployed within it. 

## Considerations
- CloudFormation is a regional service. To gather stack information across multiple regions, a separate execution is required for each region.
- The generated Excel file will contain a separate sheet/tab for each stack, making it easier to navigate and analyze stack details.
