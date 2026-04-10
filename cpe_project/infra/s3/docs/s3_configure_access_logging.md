# AWS S3 Bucket Security Improvement Script

This script is designed to enhance the security of Amazon S3 buckets in AWS. It provides functionalities to enable access logging, set bucket policies, enable versioning, and set lifecycle policies for S3 buckets. Additionally, it creates a dedicated logging bucket with specific tagging for access logs.

## Prerequisites

Before using the script, make sure you have the following:

1. AWS CLI installed and configured with the appropriate AWS profile.
2. Boto3 library installed. You can install it using pip:

   ```shell
   pip install boto3
   ```

## Script Usage

The script can be used in two ways:

1. To perform operations on a single bucket:

   ```shell
   python script_name.py --profile <AWS SSO profile> --bucket <bucket name>
   ```

2. To perform operations on all buckets in the AWS account:

   ```shell
   python script_name.py --profile <AWS SSO profile> --all
   ```

## Script Actions

The script carries out the following actions:

1. **Create Logging Bucket**: It creates an S3 bucket to store access logs. If the specified logging bucket already exists, it will not create a new one.

2. **Set Tag on Logging Bucket**: A tag with 'Category: Security' is added to the logging bucket to categorize it as a security-related resource.

3. **Enable Access Logging**: The script enables access logging for either a specified bucket (when using the `--bucket` option) or all buckets in the AWS account (when using the `--all` option). The access logs are stored in the previously created logging bucket.

4. **Set Bucket Policy**: The script sets a bucket policy to deny HTTP access to the specified bucket. The bucket policy also allows access for S3 server access logging.

5. **Enable Bucket Versioning**: Versioning is enabled for the specified bucket, ensuring that all versions of objects are retained.

6. **Set Bucket Lifecycle Policy**: The script sets a lifecycle policy for the specified bucket. The policy transitions objects to the INTELLIGENT_TIERING storage class immediately and to the GLACIER_IR storage class after 30 days of being noncurrent. It also sets an expiration policy to delete expired objects.

Please note that the script utilizes AWS SSO profiles to authenticate the session and perform the operations. Ensure that the specified AWS profile has the necessary permissions to perform these actions on the specified AWS account.

Please use this, and all scripts with caution, as it will modify the configuration of AWS resources. Always verify the script and its actions/arguments before running it in a production environment.
