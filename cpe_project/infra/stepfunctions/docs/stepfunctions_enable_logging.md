# Enable Logging on AWS Step Functions State Machine

This script enables logging on a specified AWS Step Functions state machine, allowing you to monitor the execution of your workflows.

## Requirements

- Python 3.x
- boto3 library
- AWS account with appropriate permissions for Step Functions and CloudWatch Logs

## Usage

```bash
python3 enable_logging.py -p <profile_name> -n <state_machine_name> -l <log_level> [-r <region>]
```

## Arguments
`-p`, `--profile` (Required): AWS profile name for SSO login.

`-n`, `--name` (Required): State Machine name to enable logging on.

`-l`, `--level` (Required): Log level. Accepted values are: ERROR, FATAL, OFF, ALL.

`-r`, `--region` (Optional): AWS region for the state machine.

## Features
### 1. Role and Policy Management

The script checks if a specific IAM role (`StepFunctionsCloudWatchLogsRole`) exists, and if not, creates it. It also ensures that necessary policies are attached to the role.

### 2. Log Group Creation

Creates or finds an existing CloudWatch Logs log group.

### 3. Enable Logging on State Machine

Updates the specified Step Functions state machine with the required logging configuration.

## Example

Enable logging on the state machine named "MyStateMachine" with the log level set to "ALL":

python3 enable_logging.py -p default -n MyStateMachine -l ALL

## Exceptions Handling

If the specified state machine is not found, the script prints an error message and exits gracefully.
