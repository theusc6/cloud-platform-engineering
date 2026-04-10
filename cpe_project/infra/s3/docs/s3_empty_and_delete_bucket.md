# Empty and Delete S3 Bucket Script

This script is designed to empty and delete an AWS S3 bucket. The user needs to provide an AWS profile name for SSO login and the name of the bucket they want to empty and delete. The script uses the `argparse` library to parse command-line arguments.

## Command Line Arguments

- `-p`, `--profile`: (required) The AWS profile name for SSO login.
- `-b`, `--bucket-name`: (required) The name of the bucket to empty and delete.

## Functions

1. `empty_s3_bucket(name_of_bucket)`: This function empties the specified bucket by deleting all objects within it. It lists all objects in the bucket, and if there are any, it proceeds to delete them one by one using `s3_client.delete_objects`. If the bucket is already empty, it notifies the user.

2. `delete_s3_bucket(name_of_bucket)`: This function deletes the specified bucket. It uses `s3_client.delete_bucket` to remove the empty bucket.

## Usage

The script first calls the `empty_s3_bucket` function, passing the name of the bucket provided through command-line arguments. After emptying the bucket, it prompts the user to confirm whether they want to proceed with deleting the bucket.

If the user confirms by typing 'Y', 'y', or leaving it blank and pressing Enter, the script calls the `delete_s3_bucket` function to delete the bucket. If the user responds with 'N' or 'n', the script cancels the operation. If the user provides invalid input, they will be prompted to re-enter their choice.

## Note

- Be cautious when using this script, as it can result in irreversible deletion of data. Double-check the provided bucket name before running the script to ensure you do not accidentally delete the wrong bucket or data.
- Ensure you have the appropriate permissions to empty and delete the specified bucket.
