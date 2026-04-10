
# Infrastructure Compliance Scripts

Scripts to bring AWS resources into compliance with [AWS Foundational Security Best Practices](https://docs.aws.amazon.com/securityhub/latest/userguide/fsbp-standard.html).

## Example

```bash
# Login
aws sso login --profile myorg-training

# Check script options
python s3_bucket_check.py -h
usage: s3_bucket_check.py [-h] -b BUCKET -p PROFILE

options:
  -h, --help            show this help message and exit
  -b BUCKET, --bucket BUCKET
                        AWS bucket name to check
  -p PROFILE, --profile PROFILE
                        AWS profile name for SSO login

# Run compliance check
python s3_bucket_check.py -b my-test-bucket -p myorg-training
my-test-bucket: Server-side encryption enabled.
my-test-bucket: Bucket versioning enabled.
my-test-bucket: Block public access enabled.
my-test-bucket: Tagging enabled.
```

## Services Covered

See the [Services Covered](../../README.md#services-covered) table in the main README for a full list of 22 AWS services and 58 scripts.

## AWS References

* [Amazon S3 controls](https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html)
* [Amazon EC2 controls](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html)
* [Amazon RDS controls](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html)
