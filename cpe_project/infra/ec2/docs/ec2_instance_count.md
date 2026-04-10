# AWS EC2 Instance Counter

## Description

This Python script is designed to count EC2 instances managed by AWS Config for a specified AWS profile. AWS Config is a service that enables you to assess, audit, and evaluate the configurations of your AWS resources, including EC2 instances. The script uses the AWS SDK (boto3) to retrieve the list of EC2 instances from the AWS Config service, and then prints information about each instance, such as instance type, state, AWS region, and creation time.

## Usage

To use this script, follow the steps below:

1. Install Python 3 and the required libraries if not already installed.
2. Save the script to a file named `count_ec2_instances.py`.
3. Run the script using the following command:

```bash
python3 count_ec2_instances.py --profile <profile_name>
```

Replace `<profile_name>` with your AWS profile name used for Single Sign-On (SSO) login.

## Requirements

- Python 3.x
- `boto3` library: You can install it using `pip install boto3`.

## How It Works

The script uses the `argparse` library to parse the command-line arguments, specifically the AWS profile name (`-p` or `--profile`). It creates a session using the specified AWS profile and initializes an AWS Config client object.

The script then retrieves the list of configuration aggregators using the `describe_configuration_aggregators` API call. Configuration aggregators are used to aggregate data from multiple AWS accounts and regions. However, in this script, we only use the default aggregator for simplicity.

The script performs a query to AWS Config to retrieve EC2 instances using a structured query language (SQL)-like expression. The query retrieves information such as the resource ID, resource name, resource type (EC2 instance), instance type, account ID, AWS region, instance state, and resource creation time. The results are stored in the `results` variable.

The script then prints the name of the aggregator being used and iterates through the `results` to print information about each EC2 instance. If no EC2 instances are found, it prints a message indicating that no instances were found.

## Example

Suppose you have an AWS profile named `my_aws_profile` and you want to count EC2 instances managed by AWS Config. You would run the following command:

```bash
python3 count_ec2_instances.py --profile my_aws_profile
```

The script will then retrieve the list of EC2 instances from AWS Config using the specified AWS profile. It will print information about each EC2 instance, such as its type, state, region, and creation time. If no EC2 instances are found, the script will display a message indicating that no instances were found.

Please ensure that you have appropriate AWS credentials and permissions to access AWS Config and retrieve information about EC2 instances using the provided AWS profile.
