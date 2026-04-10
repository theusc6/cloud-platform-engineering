# AWS Account Creation and Verification Script

This Python script allows you to create an AWS account in AWS ControlTower's AccountFactory and verify its existence in AWS Organizations.

## Prerequisites

Before using this script, make sure you have the following prerequisites:

 - Python 3.x installed
 - AWS CLI configured with the necessary AWS credentials and default region
 - boto3 library installed `pip install boto3`

## Usage

### Clone this repository to your local machine.

```bash
git clone https://github.com/theusc6/cloud-platform-engineering.git
```
 
### Open a terminal and navigate to the directory where the script is located.

```bash
cd cloud-platform-engineering/cpe_project/infra/controltower
```

### You can review the README.md file in the `/docs` directory to see the scripts usage...

### Login to the `myorg-master` AWS account:

```bash
aws sso login --profile myorg-master
```

### Run the script using the following command:

#### general exmple:

```bash
python create_new_account.py --profile <AWS_PROFILE_NAME> --account_email <ACCOUNT_EMAIL> --display_name <DISPLAY_NAME> --ou_name <OU_NAME>
```

#### actual example:
```bash
python create_new_account.py --profile myorg-master --account_email dl-aws-root+nms-dev@example.com --display_name myorg-nms-dev --ou_name Core
```

### Replace the placeholders with your own values:

 - <AWS_PROFILE_NAME>: The name of your AWS profile.
 - <ACCOUNT_EMAIL>: The email address for the new AWS account.
 - <DISPLAY_NAME>: The display name for the new AWS account.
 - <OU_NAME>: The name of the Organization Unit (OU) where the account should be placed.

The script will initiate the creation of the AWS account in AWS ControlTower's AccountFactory and then verify its existence in AWS Organizations.

## Extending the Script

You can extend this script to suit your specific needs. Here are some ways to customize and extend it:

 - Modify the hardcoded IAM identity email and name:
    - In the create_aws_account function, you can change the values of iam_identity_email and iam_identity_name to meet your requirements.

 - Add more custom logic:
    - You can add additional logic to the script, such as creating S3 buckets, configuring IAM roles, or attaching policies, based on your use case.

 - Error handling:
    - You can further enhance error handling by adding specific error checks and handling different types of AWS errors based on your requirements.

 - Batch account creation:
    - If you need to create multiple accounts in a batch, you can modify the script to read account details from a file or an external data source and loop through them.

 - Logging:
    - Implement a logging mechanism to keep track of the script's execution and any errors that may occur during the process.

---
