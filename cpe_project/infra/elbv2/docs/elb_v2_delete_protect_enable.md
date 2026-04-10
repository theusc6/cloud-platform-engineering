# Application Load Balancer Deletion Protection and Tagging Script

This is a Python script designed to perform two main tasks related to AWS Application Load Balancers (ALBs):

1. Enable Deletion Protection:
The script checks whether an ALB with a given name exists in the AWS account. If the ALB is found, it proceeds to enable deletion protection for that load balancer. Deletion protection ensures that the ALB cannot be accidentally deleted, preventing data loss or service disruptions.

2. Set Tags:
After enabling deletion protection, the script sets specific tags for the ALB. Tags are key-value pairs that can be assigned to AWS resources, providing additional metadata and organization. In this case, the script sets two tags for the ALB: 'Category' with the value 'NetOps' and 'Product' with the value 'Network'.

## Prerequisites

Before running the script, you need to have Python 3 and the required AWS credentials set up. The script uses the `boto3` library to interact with AWS services, so make sure you have it installed.

## Usage

To use this script, run it from the command line with the following arguments:

```bash
$ python script.py -n <ALB_NAME> -p <AWS_PROFILE>
```

Where:

- `<ALB_NAME>` is the name of the AWS Application Load Balancer you want to work with.
- `<AWS_PROFILE>` is the AWS profile name used for Single Sign-On (SSO) login, providing necessary credentials and access.

## Script Execution Flow

1. The script starts by parsing the command-line arguments using the `argparse` module, which allows specifying the ALB name (`-n`) and the AWS profile name (`-p`) when invoking the script.

2. The ALB name and AWS profile are extracted from the parsed arguments.

3. A Boto3 session is created using the specified AWS profile, and an Elastic Load Balancing (ELB) version 2 client is initialized.

4. The script attempts to confirm the existence of the ALB using the `describe_load_balancers` API call. If the ALB is not found, an appropriate error message is displayed, and the script exits.

5. If the ALB exists, the script proceeds to enable deletion protection for the ALB using the `modify_load_balancer_attributes` API call. If the operation is successful, a message indicating the successful enabling of deletion protection is displayed; otherwise, an error message is shown.

6. After enabling deletion protection, the script sets tags for the ALB using the `put_bucket_tagging` API call. The specified tags, 'Category: NetOps' and 'Product: Network', are assigned to the ALB. If the tagging operation succeeds, a success message is displayed; otherwise, an error message is shown.

## Note

- Ensure that the AWS credentials used with the specified profile have sufficient permissions to interact with Application Load Balancers and set tags on the specified ALB.
- Make sure to replace `<ALB_NAME>` and `<AWS_PROFILE>` with the appropriate values when running the script.

Be cautious while using any automation script. Enabling deletion protection on resources can have implications on managing those resources. It is essential to thoroughly test and review any script in a controlled environment before using it in a production setting.
