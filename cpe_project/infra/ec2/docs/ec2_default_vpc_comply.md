# In & Out Bound Traffic Restriction for VPC Default Security Group

## EC2.2 - VPC Default Security Group Inbound and Outbound Traffic Restriction

### Overview

This Python script is designed to modify the default security group of an Amazon Web Services (AWS) Virtual Private Cloud (VPC) to disallow both inbound and outbound traffic. By default, the AWS VPC comes with a default security group that allows all inbound and outbound traffic. This script aims to tighten the security by revoking all the inbound and outbound rules from the default security group.

### Prerequisites

1. Python 3 should be installed on the system.
2. The `boto3` library must be installed. You can install it using `pip`:

```bash
pip install boto3
```

### How to Use

Make sure you have appropriate AWS credentials set up (access key and secret key) or AWS CLI configured with proper access. The script will use the AWS CLI's configuration to determine the AWS region.

To run the script, use the following command:

```bash
python script_name.py --profile YOUR_AWS_PROFILE_NAME --vpc-id YOUR_VPC_ID
```

Replace `script_name.py` with the actual filename of the script.

- `--profile`: This argument is **required** and should be set to the AWS CLI profile name that you want to use to perform the operation. The profile should have sufficient permissions to modify security groups within the VPC.
- `--vpc-id`: This argument is **required** and should be set to the ID of the VPC whose default security group you want to modify.

### Script Logic

1. The script starts by importing required libraries - `argparse`, `boto3`, and `ClientError` from `botocore.exceptions`.
2. The `main` function is defined to perform the main task of changing the default security group settings.
3. The script uses the `argparse` module to parse command-line arguments (`--profile` and `--vpc-id`) provided by the user.
4. The script utilizes the AWS SDK for Python (`boto3`) to interact with the AWS EC2 service and modifies the default security group accordingly.
5. The main steps of the script are as follows:
   - It describes the security groups associated with the provided VPC ID and looks for the default security group.
   - If the default security group is not found, the script displays an error message and exits.
   - The script then proceeds to revoke all inbound and outbound rules from the default security group.
   - Finally, it prints a success message indicating that the default security group has been updated to disallow inbound and outbound traffic.

### Important Note

Please exercise caution when running this script, as modifying security groups may impact the accessibility and security of your AWS resources. Ensure that you fully understand the implications and have appropriate permissions before running the script.
