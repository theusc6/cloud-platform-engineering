# Enable Logging for SNS Topics

## Overview
This script enables logging for SNS Topics. It will enable logging for the following protocols:

- Lambda
- SQS
- HTTPS
- Platform Application Endpoint
- Kinesis Data Firehose

## Actions
This script takes the following actions:
- Enables logging for the specified SNS topic with a success sample rate of 50%.
- Will enable log delivery status for the above protocols
- If one does not already exist, it will create the IAM role "role-myorg-sns-logging+prod-ops" for logging as needed.

## Usage
The script can be ran with the following command:

```
python sns_enable_logging.py --profile <insert profile> --region <insert region> --topic-name <insert topic name>
```

## Target(s)
This script should be ran in any AWS account that contains an SNS topic that is not configured for any logging.

## Considerations
- This script can be modified, as needed, to enable only the logging types or rates that are desired. Security Hub will report a FAILED finding if no logging is enabled.
