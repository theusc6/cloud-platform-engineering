# S3 Bucket Size Calculator

This script is a Python program that calculates the size of an AWS S3 bucket and presents it in a human-readable format (KB, MB, GB, or TB). It uses the AWS SDK for Python (Boto3) to interact with the S3 service and fetch the size information.

## Prerequisites

Before using the script, ensure you have the following:

1. Python installed on your system.
2. AWS CLI configured with valid credentials that have permissions to access the target S3 bucket.

### Usage

The script is intended to be run from the command line and requires two arguments:

1. `-p` or `--profile`: The name of the AWS CLI profile to use for authentication. This profile should contain the necessary credentials for accessing AWS services.
2. `-b` or `--bucket-name`: The name of the S3 bucket for which you want to calculate the size.

Example usage:

```bash
python s3_get_bucket_size.py -p your_aws_profile -b your_bucket_name
```

Replace `s3_get_bucket_size.py` with the actual name of the Python script file.

### How It Works

1. The script imports necessary modules, including `argparse` for handling command-line arguments and `boto3` for interacting with AWS services.
2. It sets up an argument parser to read and validate the required `-p` (profile) and `-b` (bucket-name) arguments.
3. The script then initializes a Boto3 session using the provided profile name and creates an S3 client.
4. The main function `get_s3_bucket_size` is defined to calculate the total size of the specified S3 bucket.
5. The function uses the `list_objects_v2` method to list all objects in the bucket. It iterates through the paginated response and sums up the size of each object.
6. The total size is converted into a human-readable format using the `format_size` function.
7. The final result is printed to the console, showing the size of the S3 bucket in a readable format.

### Function Details

1. `get_s3_bucket_size(name_of_bucket)`: This function takes the name of the S3 bucket as input and calculates its size. It utilizes pagination to handle large buckets efficiently. If an error occurs during the process (e.g., invalid bucket name or authentication issues), the function catches the error and prints an appropriate error message.

2. `format_size(size_in_bytes)`: This function takes the total size of the bucket in bytes as input and converts it into a human-readable format (KB, MB, GB, or TB). It returns both the size value and the corresponding unit.

### Note

- The script assumes you have already configured the AWS CLI with appropriate credentials, and the provided profile has access to list objects in the specified S3 bucket.
- In case of any errors during execution, an error message will be printed to the console.

Remember to replace `your_aws_profile` and `your_bucket_name` with your actual AWS profile name and the S3 bucket you want to analyze.
