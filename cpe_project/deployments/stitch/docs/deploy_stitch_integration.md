
# Stitch Integration Deployment Script

This script automates the creation of an AWS Identity and Access Management (IAM) role and policy for integrating with Stitch. It allows you to create the necessary IAM resources with ease.

## Prerequisites

Before using this script, ensure that you have the following prerequisites in place:

1. AWS CLI installed and configured with the necessary AWS credentials.
2. Python 3.x installed on your system.
3. Boto3 library installed for Python. You can install it using pip:

   ```python
   pip install boto3
   ```

## Usage

1. Clone this repository to your local machine or download the script directly.

2. Open a terminal and navigate to the directory where the script is located.

3. Run the script with the following command:

   ```shell
   python create_stitch_integration.py --role-name <IAM_ROLE_NAME> --external-account-number <EXTERNAL_ACCOUNT_NUMBER> --external-id <EXTERNAL_ID> --policy-name <IAM_POLICY_NAME> --aws-profile <AWS_PROFILE>
   ```

   Replace the placeholders with your specific values:

   - `<IAM_ROLE_NAME>`: Name for the IAM role to be created.
   - `<EXTERNAL_ACCOUNT_NUMBER>`: External AWS account number for trust policy.
   - `<EXTERNAL_ID>`: External ID for trust policy.
   - `<IAM_POLICY_NAME>`: Name for the IAM policy to be created.
   - `<AWS_PROFILE>`: AWS CLI profile to use for authentication.

4. The script will create the IAM role and policy with the necessary permissions for integrating with Stitch. It will also attach a "Name" tag with the value "Stitch" to both resources for identification.

## Example

With the following **Stitch** configuration information (from Stitch)

```shell
External Account - 123456789012
External ID      - stitch_connection_199620
Role Name        - stitch_dynamodb_199620
Policy Name      - stitch_dynamodb_199620
```

Here's an example of how to run the script:

```shell
python deploy_stitch_integration.py --role-name stitch_dynamodb_199620 --external-account-number 123456789012 --external-id stitch_connection_199620 --policy-name stitch_dynamodb_199620 --aws-profile myorg-grading-engine-dev
```

## Validation

```shell
aws iam list-roles --query "Roles[?RoleName == 'stitch_dynamodb_199620'] | [0]" --profile myorg-grading-engine-dev && \
echo " ----- " && \
aws iam list-policies --query "Policies[?PolicyName == 'stitch_dynamodb_199620'] | [0]" --profile myorg-grading-engine-dev
```

### Expected Output

```shell
{
    "Path": "/",
    "RoleName": "stitch_dynamodb_199620",
    "RoleId": "AROAWXVU737QJSAUNYVGY",
    "Arn": "arn:aws:iam::123456789012:role/stitch_dynamodb_199620",
    "CreateDate": "2023-10-02T17:52:41+00:00",
    "AssumeRolePolicyDocument": {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": "arn:aws:iam::123456789012:root"
                },
                "Action": "sts:AssumeRole",
                "Condition": {
                    "StringEquals": {
                        "sts:ExternalId": "stitch_connection_199620"
                    }
                }
            }
        ]
    },
    "Description": "Role to allow stitch_dynamodb_199620 policy connections to accounts dynamodb tables",
    "MaxSessionDuration": 3600
}
 -----
{
    "PolicyName": "stitch_dynamodb_199620",
    "PolicyId": "ANPAWXVU737QOPY2KQTUI",
    "Arn": "arn:aws:iam::123456789012:policy/stitch_dynamodb_199620",
    "Path": "/",
    "DefaultVersionId": "v1",
    "AttachmentCount": 1,
    "PermissionsBoundaryUsageCount": 0,
    "IsAttachable": true,
    "CreateDate": "2023-10-02T17:51:19+00:00",
    "UpdateDate": "2023-10-02T17:51:19+00:00"
}

```

## Cleanup

To remove the IAM role and policy created by this script, you can use the AWS Management Console, AWS CLI, or other AWS management tools. Be cautious when deleting IAM resources, as it may affect your integration with Stitch.