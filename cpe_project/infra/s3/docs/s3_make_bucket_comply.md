# AWS S3 Bucket Compliance

This script is a Python program designed to automate the implementation of various security best practices for an AWS S3 bucket. It ensures that the specified S3 bucket complies with AWS Foundational Security Best Practices v1. The script uses the AWS SDK for Python (Boto3) to interact with the AWS S3 service and apply the necessary configurations.

## Prerequisites

Before using the script, ensure you have the following:

1. Python installed on your system.
2. AWS CLI configured with valid credentials that have permissions to access the target S3 bucket.

### Usage

The script is intended to be run from the command line and requires two arguments:

1. `-b` or `--bucket`: The name of the AWS S3 bucket on which the security configurations should be applied.
2. `-p` or `--profile`: The name of the AWS CLI profile to use for authentication. This profile should contain the necessary credentials for accessing AWS services.

Example usage:

```bash
python s3_make_bucket_comply.py -b your_bucket_name -p your_aws_profile
```

Replace `s3_make_bucket_comply.py` with the actual name of the Python script file.

### How It Works

1. The script imports necessary modules, including `argparse` for handling command-line arguments, `sys` for system-level functionality, and `boto3` for interacting with AWS services.

2. It sets up an argument parser to read and validate the required `-b` (bucket) and `-p` (profile) arguments.

3. The script checks if the specified bucket exists and if the user has access to it. If the bucket doesn't exist or access is denied, the script exits with an appropriate error message.

4. The script then applies several security configurations to the specified S3 bucket, as follows:

   a. **Enable Server-Side Encryption**: The script enables server-side encryption for the bucket using AES256 encryption.

   b. **Enable Bucket Versioning**: It enables versioning for the bucket, ensuring that multiple versions of objects can be stored.

   c. **Block All Public Access**: The script blocks all public access to the bucket by setting appropriate access control configurations.

   d. **Enable Bucket Logging**: It enables bucket logging, which logs all requests made to the bucket and stores the logs in a folder named 'logs/' within the same bucket.

   e. **Set Tags**: The script sets tags on the bucket, adding metadata to categorize and label the bucket. In this example, the tags 'Category: DevOps' and 'Product: S3 Bucket' are added.

### Note

- The script assumes you have already configured the AWS CLI with appropriate credentials, and the provided profile has access to modify the specified S3 bucket.
- In case of any errors during execution, appropriate error messages will be printed to the console, indicating the configuration that failed to apply.

Remember to replace `your_bucket_name` and `your_aws_profile` with the actual name of the S3 bucket you want to secure and the AWS CLI profile name with appropriate permissions.
