# Enable Point-in-Time Recovery for DynamoDB Table

## Description

This script is a Python tool that enables Point-in-Time Recovery (PITR) for a specific DynamoDB table. Point-in-Time Recovery is a feature provided by Amazon DynamoDB that allows you to restore your table to any point in time during the last 35 days. It helps protect against accidental data loss or corruption by enabling continuous backups and providing the ability to recover data to a specific moment in time.

## Usage

To use this script, follow the steps below:

1. Install Python 3 and the required libraries if not already installed.
2. Save the script to a file named `enable_point_in_time_recovery.py`.
3. Run the script using the following command:

```bash
python3 enable_point_in_time_recovery.py --profile <profile_name> --table <table_name>
```

Replace `<profile_name>` with your AWS profile name used for Single Sign-On (SSO) login, and `<table_name>` with the name of the DynamoDB table you want to enable Point-in-Time Recovery for.

## Requirements

- Python 3.x
- `boto3` library: You can install it using `pip install boto3`.

## How It Works

The script uses the `argparse` library to parse command-line arguments, specifically the AWS profile name (`-p` or `--profile`) and the DynamoDB table name (`-t` or `--table`). It then creates a session using the specified AWS profile and creates a DynamoDB client.

The `enable_point_in_time_recovery` function takes the DynamoDB client and the table name as input arguments. It attempts to enable Point-in-Time Recovery for the specified table using the `update_continuous_backups` API call. If successful, it prints the status of the Point-in-Time Recovery for the table. If an error occurs during the process, it prints an error message.

The `main` function is the entry point of the script. It calls the `parse_args` function to get the command-line arguments, creates a session using the AWS profile, and initializes a DynamoDB client. Finally, it calls the `enable_point_in_time_recovery` function with the client and table name as arguments to enable Point-in-Time Recovery for the specified table.

## Example

Suppose you have an AWS profile named `my_aws_profile` and you want to enable Point-in-Time Recovery for a DynamoDB table named `my_table`. You would run the following command:

```bash
python3 enable_point_in_time_recovery.py --profile my_aws_profile --table my_table
```

The script will then attempt to enable Point-in-Time Recovery for the `my_table` DynamoDB table using the specified AWS profile. If successful, it will print the status of the Point-in-Time Recovery for the table. If an error occurs during the process, it will display an error message.

Please ensure that you have appropriate AWS credentials and permissions to enable Point-in-Time Recovery for the specified DynamoDB table using the provided AWS profile.

Please ensure you review and understand any script before running it to ensure it aligns with your specific requirements and intended outcome.
