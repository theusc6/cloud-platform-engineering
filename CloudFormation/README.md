
# CloudFormation Templates

IaC templates for provisioning AWS resources with security best practices baked in.

## Templates

| Directory | Description |
|-----------|-------------|
| `s3/` | S3 bucket with encryption, versioning, public access blocking, logging, and SSL-only policy |
| `centralized-backup-configuration/` | Multi-account AWS Backup setup (org policy, member accounts, IAM roles) |
| `centralized-software-distributor/` | SSM Distributor for centralized package management |
| `CloudWatch/` | CloudWatch dashboard templates for monitoring |
| `aws-nuke/` | AWS Nuke configuration for account cleanup |

## Deploying a Template

```bash
# Authenticate
aws sso login --profile <your-profile>

# Deploy (example: S3 bucket)
aws cloudformation create-stack \
  --stack-name my-s3-stack \
  --template-body file://s3/s3_bucket_create.yaml \
  --parameters ParameterKey=BucketName,ParameterValue=my-secure-bucket \
  --capabilities CAPABILITY_NAMED_IAM \
  --profile <your-profile>

# Check status
aws cloudformation describe-stacks \
  --stack-name my-s3-stack \
  --profile <your-profile>
```

## Deleting a Stack

```bash
aws cloudformation delete-stack \
  --stack-name my-s3-stack \
  --profile <your-profile>
```

**Note:** Deleting a stack removes ALL resources created by that stack. Review before running.
