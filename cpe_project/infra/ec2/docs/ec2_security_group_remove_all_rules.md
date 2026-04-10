# Security Group Rules Removal Script

## Description

This script is a Python tool that remediates the AWS Control "[EC2.2] This AWS control checks that the default security group of a VPC does not allow inbound or outbound traffic." It uses the Boto3 library to remove all inbound and outbound security group rules from a specified security group in the provided AWS Single Sign-On (SSO) profile name and AWS region.

## Usage

To use this script, follow the steps below:

1. Install Python 3 and the required libraries if not already installed.
2. Save the script to a file named `remove_sg_rules.py`.
3. Run the script using the following command:

```bash
python remove_sg_rules.py --profile <profile_name> --sg_id <security_group_id>
```

Replace `<profile_name>` with your AWS Single Sign-On (SSO) profile name used for login, and `<security_group_id>` with the ID of the security group from which you want to remove all inbound and outbound rules.

By default, the script uses the `us-west-2` region. If you want to use a different AWS region, you can specify it using the `-r` or `--region` option:

```bash
python remove_sg_rules.py --profile <profile_name> --sg_id <security_group_id> --region <aws_region>
```

## Requirements

- Python 3.x
- `boto3` library: You can install it using `pip install boto3`.

## How It Works

The script uses the `argparse` library to parse the command-line arguments, specifically the AWS SSO profile name (`-p` or `--profile`), the AWS region (`-r` or `--region`), and the security group ID (`--sg_id`). It then creates a Boto3 session using the specified AWS SSO profile name and AWS region and initializes an EC2 resource object.

The `remove_sg_rules` function takes the EC2 resource object and the security group ID as input arguments. It attempts to remove all inbound and outbound rules from the specified security group using the `revoke_ingress` and `revoke_egress` methods. If successful, it prints a message indicating that all ingress and egress rules have been removed from the security group. If an error occurs during the process, it prints an error message.

The `main` function is the entry point of the script. It calls the `parse_args` function to get the command-line arguments, creates a Boto3 session using the AWS SSO profile name and region, and initializes an EC2 resource object. Finally, it calls the `remove_sg_rules` function with the EC2 resource object and security group ID as arguments to remove all inbound and outbound rules from the specified security group.

## Example

Suppose you have an AWS SSO profile named `my_aws_profile` and you want to remove all inbound and outbound rules from a security group with the ID `sg-1234567890abcdef0`. You would run the following command:

```bash
python remove_sg_rules.py --profile my_aws_profile --sg_id sg-1234567890abcdef0
```

The script will then attempt to remove all inbound and outbound rules from the specified security group using the provided AWS SSO profile and the default AWS region (`us-west-2`). If successful, it will print a message indicating that all ingress and egress rules have been removed from the security group. If an error occurs during the process, it will display an error message.

Please ensure that you have appropriate AWS credentials and permissions to modify security group rules using the provided AWS SSO profile in the specified AWS region.
