# Overview
This script will deploy the resources necessary to enable centralized logging, to Splunk, for all CloudTrail logs in the deployed region. Depsite the infrastructure (function, Kinesis Firehose, etc.) being deployed in a single region, all CloudTrail logs from all regions will be logged via the infra to Splunk requiring only a single deployment.

# Actions
This script will perform the following actions in the target security tooling account:
- Creation of a dedicated S3 bucket for the Kinesis processor.
- Configuration of a Kinesis data firehose tailored for CloudTrail logs.
- Establishment of a KMS key for data encryption and its management.
- Create the necessary IAM roles and policies
- Create a Lambda function used for data transformation
- Create necesary CloudWatch resources
  
This script will perform the following actions in the master account:
- Create a log group, if required.
- Create the subscription filter for the above log group.
User input will specify the log group to be used, the destination ARN for the Kinesis Firehose, the log format, and the filter name.
Note: This script should be ran 2nd as the necessary inputs are provided from the first script.

# Usage
The ```cloudwatch_configure_external_subscription_filter.py``` will be ran first.
```
cloudwatch_configure_external_subscription_filter.py
-profile <insert profile>
-region <insert region>
-account_id <insert account id>
```
Please note that the initializing the script will result in two additional bits of information via a user input prompt (see below). Both of these items should be provided to you by the Splunk team. They are required for successfully deployment.
- log_group_name
- destination_arn
- log_format
- filter_name

The ```kinesis_guardduty_deployment.py``` script can be ran with the following:
```
python kinesis_guardduty_deployment.py
-profile <insert profile>
-region <insert region>
-account_id <insert account id>
```
Please note that the initializing the script will result in two additional bits of information via a user input prompt (see below). Both of these items should be provided to you by the Splunk team. They are required for successfully deployment.
- HEC Token
- HTTP Endpoint URL

# Targets
This script should only be ran in the following locations:
- Script #1 will be ran against the master account, or the primary account/region where Control Tower CloudTrail logs are sent to CloudWatch.
- Script #2 will be ran against the Security Tooling account in the primary region, where the necessary infra will be configured to send CloudTrail/CloudWatch logs to Splunk.

# Considerations
- Kinesis Firehose utilizes a Lambda function (provided) for data transformation. Modificiation to the code of this function can render the logging inoperable and thus should be done only after thorough testing.
