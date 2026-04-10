# S3 Bucket Size Listing Script

This script is a Python command-line tool that allows you to list all Amazon S3 buckets and their sizes. It uses the AWS SDK for Python, known as Boto3, to interact with the AWS S3 service. The script requires the AWS credentials to be set up in the user's environment, and the AWS CLI configuration or an external configuration file is used to specify the profile name for Single Sign-On (SSO) login.

## How to Use

1. Clone or download the script to your local machine.

2. Ensure you have Python installed on your machine.

3. Install the required dependencies by running the following command in your terminal or command prompt:

    ```bash
    pip install argparse boto3
    ```

4. Run the script using the following command format:

    ```bash
    python s3_bucket_sizes.py -p <AWS_PROFILE> [-s <MIN_SIZE>] [-b]
    ```

- `-p` or `--profile`: Specifies the AWS profile name to use for authentication, which should have the required permissions to list S3 buckets and objects.

- `-s` or `--size`: (Optional) Specifies the minimum size in megabytes (MB) for objects to be included in the output. Objects smaller than this size will be excluded from the size calculation.

- `-b` or `--bucket-size-only`: (Optional) If this flag is provided, the script will only show the size of each bucket and not its individual contents.

## How it Works

1. The script uses the `argparse` library to handle command-line arguments. It requires the user to provide an AWS profile name using the `-p` option.

2. The AWS session and S3 client are initialized using the provided profile name, allowing the script to authenticate with AWS and interact with the S3 service.

3. The `-s` option (if provided) specifies a minimum object size in megabytes. Objects smaller than this size will not be included in the output.

4. The `convert_size()` function is defined to convert object sizes from bytes to a human-readable format (B, MB, GB, or TB) for better readability.

5. The script fetches a list of all S3 buckets using the S3 client.

6. For each bucket, the script retrieves the total size of the bucket and, optionally, its contents.

7. If the `--bucket-size-only` flag is provided, the script fetches the total size of the bucket only and prints the bucket name along with its size.

8. If the `--bucket-size-only` flag is not provided, the script fetches the individual objects within the bucket and calculates their cumulative size, considering only objects that meet the minimum size requirement. The list of objects is then sorted in descending order of size, and both the bucket size and individual object sizes are printed.

9. If the script encounters any errors while fetching the bucket or object information, appropriate error messages are displayed.

## Example

To list the sizes of all S3 buckets for an AWS profile named `my_aws_profile`, you would run the following command:

```bash
python s3_bucket_sizes.py -p my_aws_profile
```

To list the sizes of all S3 buckets for the same profile but considering only objects greater than or equal to 100 MB in size, you would run:

```bash
python s3_bucket_sizes.py -p my_aws_profile -s 100
```

To list only the sizes of the buckets and not the individual objects, you would run:

```bash
python s3_bucket_sizes.py -p my_aws_profile -b
```

Remember to replace `my_aws_profile` with the actual AWS profile name you want to use.
