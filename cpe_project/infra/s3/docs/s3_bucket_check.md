
# AWS S3 Bucket Security Check Script

This script is designed to check the security settings of an AWS S3 bucket to ensure it complies with AWS Foundational Security Best Practices v1. It takes in two arguments using command-line options:

## Command-line Arguments

1. `-b` or `--bucket`: (Required) The name of the AWS S3 bucket that needs to be checked for security settings.
2. `-p` or `--profile`: (Required) The name of the AWS profile to use for Single Sign-On (SSO) login to AWS.

### Functionality

1. **Check Bucket Existence**: The script first verifies whether the specified bucket exists or not. If the bucket is not found (HTTP 404), it will print a message indicating that the bucket doesn't exist and exit the script. If access is denied (HTTP 403), it will print a message indicating that access is denied to the bucket and exit the script.

2. **Check Server-Side Encryption**: The script then checks whether server-side encryption is enabled for the bucket. If encryption is enabled, it will print a message confirming the same. If encryption is not enabled, it will print an error message with the reason for the failure.

3. **Check Bucket Versioning**: The script checks whether versioning is enabled for the bucket. If versioning is enabled, it will print a message with the current status of versioning (e.g., Enabled, Suspended). If versioning is not enabled, it will print a message indicating that versioning is not enabled.

4. **Check Public Access Block Settings**: The script checks whether the public access block settings are enabled for the bucket. If the public access block is enabled, it will print a message confirming the same. If the public access block is not enabled, it will print a message indicating that public access is not blocked.

5. **Check Bucket Logging**: The script checks whether bucket logging is enabled for the bucket. If bucket logging is enabled, it will print a message confirming the same. If bucket logging is not enabled, it will print a message indicating that bucket logging is not enabled.

6. **Check Tags**: Finally, the script checks whether tags are associated with the bucket. If tags are present, it will print a message confirming the same. If no tags are set, it will print a message indicating that no tags are present for the bucket.

### Dependencies

1. `argparse`: This module is used for parsing the command-line arguments.
2. `sys`: This module provides access to some variables used or maintained by the interpreter and to functions that interact with the interpreter.
3. `boto3`: This is the AWS SDK for Python, which allows interaction with AWS services.
4. `botocore.exceptions`: This module contains exceptions raised by AWS service clients.

### How to Run the Script

To use the script, you need to have Python installed along with the required dependencies. You can run the script using the following command:

```bash
python s3_bucket_check.py -b <bucket_name> -p <profile_name>
```

Make sure to
 provide the correct `<bucket_name>` and `<profile_name>` values. The script will then check the security settings of the specified AWS S3 bucket and provide the results accordingly.
