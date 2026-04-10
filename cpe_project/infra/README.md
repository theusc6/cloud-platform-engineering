
# How to use this Repository

## Status

![example workflow](https://github.com/github/docs/actions/workflows/main.yml/badge.svg)

## Scripts here are designed to bring legacy assets in AWS into compliance with AWS conventions

### Example

```bash
# login
NY-IT-MAC-01:infra user$aws sso login --profile myorg-training

# Execute script with required arguments
NY-IT-MAC-01:infra user$ python s3-bucket-comply.py -h
usage: s3-bucket-comply.py [-h] -b BUCKET -p PROFILE

options:
  -h, --help            show this help message and exit
  -b BUCKET, --bucket BUCKET
                        AWS bucket name to apply changes
  -p PROFILE, --profile PROFILE
                        AWS profile name for SSO login

NY-IT-MAC-01:infra user$ python s3-bucket-comply.py -b user-test-1az -p myorg-training
user-test-1az: Bucket exists.
user-test-1az: Server-side encryption enabled.
user-test-1az: Bucket versioning enabled.
user-test-1az: Block public access enabled.
user-test-1az: Tagging enabled.
```

### What is in here

```bash
.
├── README.md
├── ec2
│   ├── ec2-list-sg-sso.py
│   ├── ec2_default_vpc_comply.py
│   ├── ec2_instance_count.py
│   └── vpc_alb_delete_protect_enable.py
├── other
│   ├── aws_add_tags.py
│   ├── aws_create_pipeline_role.py
│   ├── aws_fsx_create.py
│   ├── ecs_readonly_root_comply.py
│   └── iam-all-account-list.py
└── s3
    ├── s3-public-deny.py
    ├── s3-public-restrict.py
    ├── s3_bucket_create.py
    ├── s3_bucket_create_1.py
    ├── s3_empty_and_delete_bucket.py
    ├── s3_get_all_bucket_sizes.py
    ├── s3_get_bucket_size.py
    └── s3_make_bucket_comply.py

4 directories, 18 files
```

### AWS Conventions

* [Amazon Simple Storage Service controls](https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html)
