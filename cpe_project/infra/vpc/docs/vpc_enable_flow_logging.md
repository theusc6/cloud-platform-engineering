# VPC Flow Logging Enabler
This script enables VPC flow logging with specific settings for a given VPC. It will send logs to the S3 bucket created by this script along with all required dependencies (IAM roles, bucket compliance configurations, etc.).

## Usage

python3 vpc_enable_flow_logging.py -p <profile_name> -r <region_name> -v <vpc_id>

## Script Functionality

1. Parses command-line arguments.
2. Creates an IAM role with specific permissions.
3. Creates an S3 bucket for the VPC flow logs.
4. Enables VPC flow logging.

### Function Descriptions
- parse_args(): Parses the command-line arguments.
- create_iam_role(session): Creates the necessary IAM role. Returns the ARN.
- create_s3_bucket(session, bucket_name, account_id, region): Creates an S3 bucket with specific settings for VPC flow logs.
- enable_vpc_flow_logging(params): Enables VPC flow logging for the given VPC ID.
- main(): The main function of the script.

## Prerequisites
- AWS CLI
- Boto3 library
- Python 3.x
  
## Notes
Ensure you have the required IAM permissions for each of the actions taken by this script.

It's recommended to test this script in a development or staging environment before running it in a production environment.
