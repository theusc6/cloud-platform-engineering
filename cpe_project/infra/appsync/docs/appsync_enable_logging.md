# Enable AWS AppSync Logging

## Overview
This script will enable logging for AWS AppSync to CloudWatch.

## Actions
- If one does not exist, will create IAM role required for CloudWatch logging
- Enables logging for the AppSync API to CloudWatch with log level "All"

## Usage
The script can be ran with the following:
```
python appsync_enable_logging.py --profile <insert profile> --region <insert region> --api <insert appsync api id>
```

## Targets
This script should be ran in any account that contains AppSync resources that are not being logged.

## Considerations
N/A
