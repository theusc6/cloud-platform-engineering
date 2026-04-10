# AWS Backup Cost Estimation Script

## Overview
This script queries AWS resources across multiple accounts and regions to estimate future backup costs. It collects actual resource sizes that would be backed up by AWS Backup and exports comprehensive inventory data to an Excel file for cost analysis and planning.

## Actions
This script performs the following actions:
- Queries AWS resources across specified accounts and regions that are eligible for AWS Backup
- For each resource type, collects detailed information including:
DynamoDB Tables

Table Name - The name of the DynamoDB table
Status - Current table status (e.g., ACTIVE, CREATING)
Size (Bytes) - Table size in bytes
Size (GB) - Table size in gigabytes
Item Count - Number of items in the table
Billing Mode - Billing configuration (PROVISIONED or PAY_PER_REQUEST)
Region - AWS region where the table exists
Account ID - AWS account identifier
Account Name - Descriptive name of the account

EFS File Systems

File System ID - Unique identifier for the EFS file system
Name - Name tag of the file system
Lifecycle State - Current state (e.g., available, creating)
Size (Bytes) - File system size in bytes
Size (GB) - File system size in gigabytes
Performance Mode - Performance configuration (generalPurpose or maxIO)
Encrypted - Whether encryption is enabled
Region - AWS region where the file system exists
Account ID - AWS account identifier
Account Name - Descriptive name of the account

EBS Volumes

Volume ID - Unique identifier for the EBS volume
Name - Name tag of the volume
Size (GB) - Volume size in gigabytes
Volume Type - Type of volume (e.g., gp3, io2, standard)
State - Current volume state (e.g., available, in-use)
Encrypted - Whether encryption is enabled
Attached Instance - EC2 instance ID if attached, or Not Attached
Region - AWS region where the volume exists
Account ID - AWS account identifier
Account Name - Descriptive name of the account

RDS Instances

DB Instance ID - Identifier for the RDS instance
DB Name - Name of the database
Size (GB) - Allocated storage in gigabytes
Status - Current instance status (e.g., available, backing-up)
Engine - Database engine (e.g., postgres, mysql, oracle)
Engine Version - Version of the database engine
Instance Class - Instance type (e.g., db.t3.micro)
Multi-AZ - Whether Multi-AZ deployment is enabled
Encrypted - Whether storage encryption is enabled
Region - AWS region where the instance exists
Account ID - AWS account identifier
Account Name - Descriptive name of the account

Aurora Clusters

Cluster ID - Identifier for the Aurora cluster
Size (GB) - Allocated storage in gigabytes
Status - Current cluster status (e.g., available, backing-up)
Engine - Database engine (e.g., aurora-mysql, aurora-postgresql)
Engine Version - Version of the database engine
Multi-AZ - Whether Multi-AZ deployment is enabled
Encrypted - Whether storage encryption is enabled
Region - AWS region where the cluster exists
Account ID - AWS account identifier
Account Name - Descriptive name of the account

FSx for Windows File Systems

File System ID - Unique identifier for the FSx file system
Size (GB) - Storage capacity in gigabytes
Lifecycle - Current lifecycle state (e.g., AVAILABLE, CREATING)
Storage Type - Type of storage (e.g., SSD, HDD)
Region - AWS region where the file system exists
Account ID - AWS account identifier
Account Name - Descriptive name of the account

FSx for Lustre File Systems

File System ID - Unique identifier for the FSx file system
Size (GB) - Storage capacity in gigabytes
Lifecycle - Current lifecycle state (e.g., AVAILABLE, CREATING)
Storage Type - Type of storage (e.g., SSD, HDD)
Region - AWS region where the file system exists
Account ID - AWS account identifier
Account Name - Descriptive name of the account

DocumentDB Clusters

Cluster ID - Identifier for the DocumentDB cluster
Size (GB) - Allocated storage in gigabytes
Status - Current cluster status (e.g., available, backing-up)
Engine - Database engine (always docdb)
Encrypted - Whether storage encryption is enabled
Region - AWS region where the cluster exists
Account ID - AWS account identifier
Account Name - Descriptive name of the account

Neptune Clusters

Cluster ID - Identifier for the Neptune cluster
Size (GB) - Allocated storage in gigabytes
Status - Current cluster status (e.g., available, backing-up)
Engine - Database engine (always neptune)
Encrypted - Whether storage encryption is enabled
Region - AWS region where the cluster exists
Account ID - AWS account identifier
Account Name - Descriptive name of the account

Storage Gateway Volumes

Volume ARN - Amazon Resource Name for the volume
Volume Type - Type of Storage Gateway volume
Size (GB) - Volume size in gigabytes
Gateway ARN - ARN of the parent gateway
Region - AWS region where the volume exists
Account ID - AWS account identifier
Account Name - Descriptive name of the account

S3 Buckets

Bucket Name - Name of the S3 bucket
Size (Bytes) - Bucket size in bytes (StandardStorage class)
Size (GB) - Bucket size in gigabytes
Region - AWS region where the bucket exists
Account ID - AWS account identifier
Account Name - Descriptive name of the account
The collected data is exported into an Excel document named AWS_Backup_Data_Collector_<ENVIRONMENT>.xlsx, with each resource type on a separate sheet for easy analysis and cost calculation.

## Usage
The script can be executed with the following command:

```
python3 aws_backup_data_collector.py --profile <profile_name> --environment <env>
```
--profile_name or -p (required): AWS profile name to use for authentication
--environment or -e (optional): Environment filter - choices are prod, dev, uat, or org (default: org)

prod: Queries only production accounts
dev: Queries only development accounts
uat: Queries only UAT/shared accounts
org: Queries all accounts in the organization


--master_account_id or -id (optional): Master account ID (default: 123456789012)
--master_account_name or -n (optional): Master account name (default: account-name)

## Targets
This script should be run against an AWS Organization to inventory all backup-eligible resources across member accounts. It uses the OrganizationAccountAccessRole to assume roles in member accounts for cross-account access.

### Supported Regions
us-east-1
us-west-2
us-east-2
eu-west-2
ap-southeast-1
ap-east-1

## Considerations
- Cross-Account Access: The script requires the OrganizationAccountAccessRole to be present in all member accounts with appropriate permissions to read resource metadata.
- Regional Services: Most services are regional, so the script iterates through all specified regions in each account. S3 is queried globally but bucket regions are identified.
- S3 Metrics: S3 bucket sizes are retrieved from CloudWatch metrics for StandardStorage class only, using data from the last 24 hours.
- Permissions Required: The execution role needs read-only permissions for all queried services: DynamoDB, EFS, EC2 (for EBS), RDS, FSx, DocumentDB, Neptune, Storage Gateway, S3, CloudWatch, STS, and Organizations.
- Performance: Execution time will vary based on the number of accounts, regions, and resources. Large organizations may take several minutes to complete.
- Cost Estimation: The output provides raw storage data that can be used with AWS Backup pricing calculator to estimate backup costs based on backup frequency and retention requirements.
- Environment Filtering: When filtering by environment, only accounts explicitly listed in the corresponding account lists (PROD_ACCOUNTS, DEV_ACCOUNTS, UAT_ACCOUNTS) will be scanned. Please be sure to add or remove as necessary when the environment is updated.
