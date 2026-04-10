# S3 Bucket Versioning Manager

This script automates the process of enabling versioning for AWS S3 buckets using the AWS SDK for Python (Boto3).

## Usage

1. Install the required Python package by running:

   ```sh
   pip install boto3
   ```

2. Run the script using the following command:

   ```sh
   python s3_bucket_version_enable.py -p <AWS_PROFILE_NAME>
   ```

   Replace `<AWS_PROFILE_NAME>` with the name of your AWS profile for Single Sign-On (SSO) login.

## What It Does

1. Parses the command-line arguments to specify the AWS profile for SSO login.

2. Sets up a session using the specified AWS profile.

3. Uses the AWS SDK to list all S3 buckets in the account.

4. Checks if versioning is already enabled for each bucket.

5. If versioning is not enabled, it enables versioning for the bucket.

6. Prints messages indicating the status of versioning for each bucket.

7. Handles any errors that occur during the process and provides relevant error messages.

This script helps ensure consistent versioning across S3 buckets, enhancing data protection and management practices.