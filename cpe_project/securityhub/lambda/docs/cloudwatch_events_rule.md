# AWS CloudWatch Event Rule Creation Script

## Overview

This script is designed to create an AWS CloudWatch Event Rule for automating the execution of the SecurityHub findings export Lambda function. The rule is scheduled to run on the first day of every month at midnight. The script also adds an event target to the rule, specifying the Lambda function that will be triggered by the rule.

## Prerequisites

- AWS CLI configured with necessary permissions or valid AWS credentials in the environment.
- Python 3.x installed.

## Usage

1. Clone or download this repository.

2. Install the required Python packages using the following command:

   ```shell
   pip install boto3
   ```

3. Replace the placeholder values in the script with actual values:
   - `LAMBDA_ARN`: Replace with the ARN of your Lambda function.

4. Run the script using the following command:

   ```shell
   python cloudwatch_events_rule.py
   ```

5. The script will create a CloudWatch Event Rule named `Export-Security-Hub-Findings-Monthly` and configure it to run the specified Lambda function on the first day of every month at midnight.

6. Check the script's output for success messages indicating the successful creation of the rule and event target.

## Script Details

- The script uses the `boto3` library to interact with AWS services.
- It creates a CloudWatch Event Rule with the specified name and description.
- The rule is configured to run on the first day of every month at midnight using a `cron` expression.
- The rule's state is set to `ENABLED` to activate it.
- An event target is added to the rule, specifying the Lambda function ARN.

## Notes

Make sure to replace the placeholder values, such as `LAMBDA_ARN`, with actual values relevant to your environment. Adjust the content as needed to fit your repository's structure and context.
