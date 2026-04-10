# Ansible Access Default Security Group Creation

## Description

This script creates a default security group for Ansible access in AWS. The purpose of this script is to simplify the process of setting up security groups in VPCs that have instances where Ansible will be used for automation and configuration management. The script lists all VPCs in the specified AWS profile and counts the number of instances in each VPC. It then prompts the user to confirm whether they want to create the security group in VPCs that have instances. If confirmed, the script creates the security group and allows SSH access (TCP port 22) from specific CIDR blocks.

## Usage

To use this script, follow the steps below:

1. Install Python 3 and the required libraries if not already installed.
2. Save the script to a file named `create_ansible_security_group.py`.
3. Run the script using the following command:

```bash
python3 create_ansible_security_group.py --profile <profile_name>
```

Replace `<profile_name>` with your AWS profile name used for Single Sign-On (SSO) login.

## Requirements

- Python 3.x
- `boto3` library: You can install it using `pip install boto3`.

## How It Works

The script uses the `argparse` library to parse the command-line arguments, specifically the AWS profile name (`-p` or `--profile`). It creates a session using the specified AWS profile and initializes an EC2 client object using the session.

It then retrieves all VPCs and counts the number of instances in each VPC. The script stores this information in the `vpcs_with_instances` dictionary, where the VPC ID is the key, and the number of instances is the value.

The script then prints the list of VPCs found in the specified AWS profile along with the number of instances in each VPC.

The user is prompted to confirm whether they want to create the security group in VPCs that have instances. If the user's input is anything other than 'n' or 'N', the script proceeds to create the security group and allow SSH access (port 22) from specific CIDR blocks. The security group is named 'ssh-rfc-1819' and is described as 'Security group for Ansible access'.

For each VPC with instances, the script attempts to create the security group using the `create_security_group` API call. If successful, it prints the security group ID and the VPC ID where it was created.

The script then uses the `authorize_security_group_ingress` API call to allow inbound SSH traffic from specific CIDR blocks: '172.16.0.0/12', '10.0.0.0/8', and '192.168.0.0/16'.

Finally, the script prints a list of VPCs where the security group was successfully added along with the number of instances in each VPC. If the user chooses not to create the security group, the script informs them that no security groups were created.

## Example

Suppose you have an AWS profile named `my_aws_profile` and you want to create the default Ansible security group. You would run the following command:

```bash
python3 create_ansible_security_group.py --profile my_aws_profile
```

The script will then list all VPCs in the `my_aws_profile` AWS profile and count the number of instances in each VPC. It will prompt you to confirm whether you want to create the security group in VPCs that have instances. If confirmed, it will create the security group and allow SSH access from specific CIDR blocks. The script will print the VPCs where the security group was added and the number of instances in each VPC. If you choose not to create the security group, the script will inform you that no security groups were created.

Please ensure that you have appropriate AWS credentials and permissions to create security groups and modify VPC settings using the provided AWS profile.

Please ensure you review and understand any script before running it to ensure it aligns with your specific requirements and intended outcome.
