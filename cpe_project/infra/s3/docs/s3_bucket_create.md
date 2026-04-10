# AWS S3 Bucket Configuration Script

This script is designed to create a compliant AWS S3 bucket with specific configurations. It utilizes the Boto3 library to interact with the AWS S3 service and requires an AWS profile with appropriate permissions for the specified actions.

## Prerequisites

Before running the script, make sure you have the following:

1. AWS CLI installed and configured with the appropriate AWS profile.
2. Boto3 library installed. You can install it using pip:

   ```shell
   pip install boto3
   ```

## Script Usage

To execute the script, use the following command in your terminal or command prompt:

```shell
python script_name.py -b BUCKET_NAME -p PROFILE_NAME [-f FOLDER_NAME]
```

Replace `script_name.py` with the actual name of the Python script file. The script requires two mandatory arguments and one optional argument:

1. `-b` or `--bucket`: The name of the AWS S3 bucket you want to create. This argument is required.
2. `-p` or `--profile`: The AWS profile name used for Single Sign-On (SSO) login. This argument is required.
3. `-f` or `--folder`: (Optional) The name of the folder to create within the newly created bucket.

## Script Actions

The script performs the following actions:

1. **Create Bucket**: It creates an S3 bucket with the specified name in the 'us-west-2' AWS region. If the bucket already exists and is owned by you, the script will print a message and exit gracefully.

2. **Create Folder** (Optional): If the `-f` or `--folder` argument is provided, the script creates a folder within the newly created bucket.

3. **Set Expiration Policy**: The script sets a lifecycle configuration for the contents of the folder (if created). The objects within the folder will expire after 365 days.

4. **Enable Server-Side Encryption**: Server-side encryption using AES256 is enabled for the bucket.

5. **Enable Bucket Versioning**: Versioning is enabled for the bucket to keep track of object versions.

6. **Block Public Access**: Public access to the bucket is blocked to ensure privacy and security.

7. **Enable Bucket Logging**: Logging is enabled for the bucket to capture access logs. The logs are stored in the same bucket under the 'logs/' prefix.

8. **Set Tags**: The script sets two tags, 'Category' and 'Product', for the bucket to categorize it as 'DevSecOps' and identify it as an 'S3 Bucket', respectively.

If any of the actions fail due to client errors, appropriate error messages will be printed.

Please ensure you have the necessary permissions to perform these actions on the specified AWS account and that the AWS CLI is properly configured with the correct AWS profile.

Note: It's essential to exercise caution when executing this script, as it performs several configurations and changes to your AWS resources. Make sure you thoroughly understand the script and its implications before running it.
