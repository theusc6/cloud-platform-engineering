# Update S3 Bucket Policies to Require SSL

This script is designed to update AWS S3 bucket policies to require SSL (Secure Sockets Layer) for accessing the bucket. This is done to enhance security in accordance with SecurityHub S3.5 best practices.

## Command Line Arguments

- `-p`, `--profile`: (required) The AWS profile name for SSO login.
- `-a`, `--all-buckets`: If set, the script will update policies for all buckets in the AWS account.
- `-b`, `--bucket-name`: The name of a specific bucket to update the policy.

## Function - `policy_exists(existing_policy, new_policy)`

This function checks if the new SSL policy already exists in the existing bucket policy. It compares each policy statement in the existing policy with the new policy statement to determine if it's already present.

## Function - `update_bucket_policy(name_of_bucket)`

This function updates the policy of a specific bucket to require SSL. It first retrieves the existing bucket policy using `s3_client.get_bucket_policy`. If the policy exists, it checks if the SSL policy already exists using the `policy_exists` function. If it doesn't exist, the new SSL policy statement is appended to the existing policy, and the updated policy is set using `s3_client.put_bucket_policy`. If no policy exists for the bucket, it creates a new policy with the SSL requirement.

## Function - `get_all_bucket_names()`

This function retrieves a list of all bucket names in the AWS account using `s3_client.list_buckets`.

## Usage

If the `--all-buckets` option is provided, the script retrieves all bucket names using `get_all_bucket_names()` and iterates through each bucket to update its policy with SSL requirement.

If the `--bucket-name` option is provided, the script updates the policy of the specified bucket.

If neither `--all-buckets` nor `--bucket-name` options are provided, the script displays a message to the user, indicating that they need to use one of the options.

## Note

- The script requires AWS credentials with sufficient permissions to update S3 bucket policies. Make sure the specified AWS profile has the necessary access rights.
- Be cautious when updating bucket policies, as misconfigurations can lead to access issues for applications or users relying on the S3 bucket. Always review the changes before applying them in a production environment.
