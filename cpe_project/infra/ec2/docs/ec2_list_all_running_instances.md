# EC2 Instance Listing Script

## Description

This script is a Python tool that lists all running EC2 instances from the audit account in AWS. It retrieves EC2 instances from the specified AWS profile (audit account) using AWS Config service and prints out relevant information about each running instance, such as instance ID, instance type, and state.

## Usage

To use this script, follow the steps below:

1. Install Python 3 and the required libraries if not already installed.
2. Save the script to a file named `list_running_ec2_instances.py`.
3. Run the script using the following command:

```bash
python3 list_running_ec2_instances.py -p <profile_name> [-i <instance_name>]
```

Replace `<profile_name>` with your AWS profile name used for Single Sign-On (SSO) login. The optional argument `-i` or `--instance-name` can be used to specify a particular EC2 instance name to search for.

## Requirements

- Python 3.x
- `boto3` library: You can install it using `pip install boto3`.

## How It Works

The script uses the `argparse` library to parse the command-line arguments, specifically the AWS profile name (`-p` or `--profile`) and the optional EC2 instance name (`-i` or `--instance-name`). It then calls the `search_ec2_instances` function to search for running EC2 instances matching the provided instance name. If no instance name is provided, it lists all running EC2 instances.

The `search_ec2_instances` function retrieves the AWS account ID associated with the given profile using AWS Security Token Service (STS). It then constructs an expression to query AWS Config for running EC2 instances. The function uses the AWS Config service to select aggregate resource configurations for EC2 instances that are running. The configuration aggregator name is determined based on the AWS account ID to use the appropriate aggregator for the audit account.

After retrieving the relevant information for running EC2 instances, the script prints the output in a human-readable format, displaying the instance ID, instance type, and state for each matching instance. If no matching instances are found, it displays a message indicating that no instances were found.

## Example

Suppose you have an AWS profile named `audit_account` for the audit AWS account, and you want to list all running EC2 instances in the audit account. You would run the following command:

```bsh
python3 list_running_ec2_instances.py -p audit_account
```

The script will then search for all running EC2 instances in the specified audit account and print out relevant information for each instance, such as instance ID, instance type, and state.

If you want to search for a specific EC2 instance by name, you can include the `-i` or `--instance-name` argument followed by the instance name. For example:

```bash
python3 list_running_ec2_instances.py -p audit_account -i my_instance_name
```

The script will then search for the running EC2 instance with the specified name (`my_instance_name`) in the audit account and print out its information if found. If no matching instances are found, it will display a message indicating that no instances were found.

Please ensure that you have appropriate AWS credentials and permissions to access AWS Config and retrieve information about EC2 instances using the provided AWS profile in the audit account.
