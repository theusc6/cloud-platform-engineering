
# AWS CloudFormation Template: Secure S3 Bucket

This CloudFormation template creates an Amazon S3 bucket with security measures to ensure the confidentiality and integrity of stored objects. The template sets up server-side encryption, versioning, lifecycle policies, public access restrictions, and logging.

## Resources Created

### S3 Bucket

A new Amazon S3 bucket is created with the following configurations:

- Bucket encryption using AES256 server-side encryption by default.
- Lifecycle policy to expire noncurrent versions of objects after 365 days.
- Versioning enabled to maintain historical versions of objects.
- Public access is blocked to prevent unauthorized access.
- Server access logs are enabled to record requests to the bucket.

### S3 Bucket Policy

An S3 bucket policy is attached to the created bucket with the following restrictions:

- All actions on objects in the bucket are denied unless the request is made using SSL/TLS.

## How to Use

1. Make sure you have an AWS account and the AWS CLI installed.

2. Save the provided CloudFormation template to a file, for example, `secure-s3-bucket-template.yaml`.

3. Deploy the template using the AWS CLI:
   ```bash
   aws cloudformation create-stack --stack-name SecureS3BucketStack --template-body file://s3_bucket_create.yaml --parameters ParameterKey=BucketName,ParameterValue=my-secure-bucket
   ```

   Replace `my-secure-bucket` with the desired name for your S3 bucket.

4. Wait for the stack creation to complete.

5. Once the stack is created, you can access your new secure S3 bucket using the AWS Management Console, AWS SDKs, or the AWS CLI.

## Parameters

- `BucketName` (Optional): The desired name for the S3 bucket. If not provided, the default value "my-test-bucket" will be used.

## Cleaning Up

To delete the resources created by this CloudFormation stack, run the following command:

```bash
aws cloudformation delete-stack --stack-name SecureS3BucketStack
```
