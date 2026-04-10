# Create DevOps CICD Pipeline Role in AWS

This script simplifies the process of creating the required DevOps Continuous Integration and Continuous Deployment (CICD) pipeline role in AWS. By using the Boto3 library, it enables users to automate the creation of this essential role for orchestrating DevOps workflows.

## Overview

The purpose of this script is to streamline the creation of a dedicated IAM role that is essential for setting up DevOps CICD pipelines. This role is designed to be assumed by specific AWS principals, facilitating the secure execution of pipeline tasks.

## How to Use

1. Replace the `AWS profile name for SSO login` placeholder with the appropriate AWS profile name in the script.

2. Run the script using a Python interpreter, ensuring you have the required dependencies installed.

## Script Execution

The script performs the following actions:

1. Parses the command-line arguments to obtain the AWS profile name.

2. Establishes a connection to AWS using the Boto3 library and the provided profile.

3. Creates the required IAM role named `devops-github-service-role`.

4. Attaches the `AWSCodePipelineRole` policy to the role, enabling it to perform pipeline-related actions.

5. Adds tags to the role, categorizing it as `DevOps` and associated with the `Pipeline` product.

6. Prints the Amazon Resource Name (ARN) of the created role.

## Note

- This script simplifies the process of creating the DevOps CICD pipeline role in AWS, eliminating the need for manual setup.
- The `AssumeRolePolicyDocument` specifies the AWS principals that are allowed to assume the role, enhancing security.
- The attached `AWSCodePipelineRole` policy grants the role the necessary permissions for working with AWS CodePipeline.
- Custom tags can be added or modified in the `tags` list to match your organization's tagging conventions.
