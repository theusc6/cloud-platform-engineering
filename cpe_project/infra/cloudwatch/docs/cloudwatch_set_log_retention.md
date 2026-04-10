# Configuring CloudWatch Logs Retention Period

## Overview
This script will set the CloudWatch logs retention period to 365 days (1 year). This is the minimum compliance requirement as set forth by Security Hub rule CloudWatch.16.

## Actions
This script will perform the following actions:
- Set retention period for cloudwatch log group to 365 days (1 year)

## Usage
This script can be ran with the below command:

```
python cloudwatch_set_log_retention.py --profile <insert profile> --region <insert region> --log-group-name <insert log group name>
```

## Targets
This script should target any AWS Account that contains a CloudWatch log group that is not compliant with minimum requirements.

## Considerations
- If need be, the "retentionInDays" variable can be modified to reflect the required number of days to retain logs (if not 365, which is the default)
