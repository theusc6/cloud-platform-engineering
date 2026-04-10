# AWS S3 Bucket Versioning and Lifecycle Policy Script

This script is designed to enable versioning and set a lifecycle policy for AWS S3 buckets. The script allows the user to apply these settings to either a single specified S3 bucket or to all buckets in their AWS account.

## Command Line Arguments

- `-p`, `--profile`: (required) The AWS profile name for SSO login.
- `-b`, `--bucket`: The name of a single bucket that needs to be modified.
- `-a`, `--all`: If set, the script will modify all buckets in the AWS account.

### Example Usage

To enable versioning and set a lifecycle policy for a single bucket:

```shell
python3 script_name.py --profile my_profile --bucket my_bucket
```

To enable versioning and set a lifecycle policy for all buckets in the AWS account:

```shell
python3 script_name.py --profile my_profile --all
```

### Modules Used

- `argparse`: Used for parsing command line arguments.
- `boto3`: Used for interacting with AWS services, particularly the S3 service.
- `botocore.exceptions`: Used for handling exceptions that may arise from Boto3 operations.

### Functions

1. `enable_bucket_versioning(s3_client, bucket_name)`: This function enables versioning for the specified S3 bucket if it's not already enabled. If the versioning status is not 'Enabled', it sets the versioning status to 'Enabled'.

2. `set_bucket_lifecycle_policy(s3_client, bucket_name, lifecycle_policy)`: This function sets a lifecycle policy for the specified S3 bucket. The lifecycle policy defines actions to be taken on objects in the bucket after specified durations. It includes transitioning objects to different storage classes, cleaning up incomplete multipart uploads, and setting expiration rules.

### Main Function - `main()`

The main function parses the command-line arguments to determine the AWS profile to use and whether to modify a single bucket or all buckets. It then establishes an AWS session using the provided profile, creates an S3 client, and sets the lifecycle policy to be applied.

If the `--all` option is specified, the script lists all the buckets in the AWS account, enables versioning, and sets the lifecycle policy for each bucket. If the `--bucket` option is specified, it only applies the changes to the specified bucket.

### Lifecycle Policy

The lifecycle policy defined in the script specifies the following rules:

- **Rule ID**: 'a-securityhub-s3.13-default-lifecycle-policy'
- **Status**: Enabled (to activate the policy)
- **Filter**: Applies to all objects in the bucket (prefix empty)
- **Transitions**: Objects will transition to the 'INTELLIGENT_TIERING' storage class immediately (0 days after creation)
- **NoncurrentVersionTransitions**: Noncurrent versions (older versions) will transition to 'GLACIER_IR' storage class after 30 days
- **Expiration**: Objects with an expired delete marker will be deleted
- **NoncurrentVersionExpiration**: Noncurrent versions (older versions) will be deleted after 180 days, keeping at least one newer noncurrent version.
- **AbortIncompleteMultipartUpload**: Incomplete multipart uploads will be aborted after 30 days.

**Note:** This script is to be used with caution as it may apply irreversible actions like deleting objects and aborting multipart uploads. It is recommended to thoroughly test the script in a safe environment before running it in a production AWS account.
