# AWS VPC Report Script

This Python script interacts with AWS services using the `boto3` library to retrieve and report comprehensive information about AWS VPCs (Virtual Private Clouds). It communicates with multiple AWS accounts and regions, fetches VPC details including flow logs configuration, subnet information, and networking components, then generates a detailed report in an Excel spreadsheet.

## Features

- Retrieves comprehensive VPC details from multiple AWS accounts and regions
- Analyzes VPC Flow Logs configuration and status across all VPCs
- Collects subnet information including public/private subnet classification
- Identifies networking components (Internet Gateways, NAT Gateways)
- Distinguishes between owned and shared VPCs
- Excludes suspended accounts and generates reports for active accounts
- Stores VPC details in a pandas DataFrame with comprehensive metadata
- Generates detailed summary tables with statistics by region and account
- Exports VPC details and summary tables to separate Excel sheets

## Usage
`python vpc_report_script.py --profile_name <AWS_PROFILE_NAME> [OPTIONS]`

# Command line arguments
- profile_name (required): Name of the AWS profile configured in your ~/.aws/config file
- master_account_id (optional): AWS Master account ID (default: "123456789012")
- master_account_name (optional): AWS Master account name (default: "myorg-master")

`--profile_name (required): Name of the AWS profile configured in your ~/.aws/config file --master_account_id (optional): AWS Master account ID (default: "123456789012") --master_account_name (optional): AWS Master account name (default: "myorg-master")`

## Output

The script generates an Excel file AWS_VPC_Report-AllRegions.xlsx containing two sheets:

# VPC Details Sheet

Contains comprehensive information for each VPC including:

- VPC ID, Name, State, and Default status
- Ownership information (Owner ID and Ownership Status)
- CIDR block configurations
- Subnet analysis (total count, public/private breakdown)
- Network gateway information
- Flow Logs configuration and status
- Regional and account information

# Summary Sheet

Provides aggregated statistics including:

- Total VPC counts by ownership, type, and region
- Flow Logs enablement statistics
- Subnet distribution across accounts and regions
- Per-account and per-region breakdowns