# AWS Security Group Management Script

This Python script uses the Boto3 library to manage AWS security groups. It creates a copy of a specified security group, adds specific tags to the copied group, and then removes all inbound and outbound rules from the copied group.

## How it Works

The script performs the following steps:

1. It creates a copy of the specified security group in the same VPC.
2. It copies all inbound and outbound rules from the original security group to the copied one.
3. It adds specific tags to the copied security group.
4. It removes all inbound and outbound rules from the copied security group.

## Usage

You can run this script from the command line with the following arguments:

- `--profile`: The AWS SSO profile name (required)
- `--region`: The AWS region (default is 'us-west-2')
- `--sg_id`: The AWS security group ID (required)

Here's an example of how to run the script:

```bash
python vpc_default_sg_copy_and_clear.py --profile myorg-training --sg_id sg-0a51b6035d3083de5
```

To see all options, simply run it with `-h` 

```bash
usage: vpc_default_sg_copy_and_clear.py [-h] -p PROFILE [-r REGION] --sg_id SG_ID

Copy and clear a specified AWS security group

options:
  -h, --help            show this help message and exit
  -p PROFILE, --profile PROFILE
                        AWS SSO profile name
  -r REGION, --region REGION
                        AWS region
  --sg_id SG_ID         AWS security group ID

```

or no arguments...

```bash
usage: vpc_default_sg_copy_and_clear.py [-h] -p PROFILE [-r REGION] --sg_id SG_ID
vpc_default_sg_copy_and_clear.py: error: the following arguments are required: -p/--profile, --sg_id
```

### expected output from a successful execution

```bash
user@workstation vpc % python vpc_default_sg_copy_and_clear.py --sg_id sg-0a51b6035d3083de5 -p myorg-training
2023-10-13 10:02:37,920 - INFO - Successfully created a copy of security group 'sg-0a51b6035d3083de5', added tags, and cleared all rules from the original security group.
```
