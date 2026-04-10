# Overview
This script will deploy the resources necessary to enable centralized logging, to Splunk, for all Guard Duty logs in the deployed region.

# Actions
This script will perform the following actions:
- Creation of a dedicated S3 bucket for the Kinesis processor.
- Establishment of a KMS key for data encryption and its management.
- Setup of an IAM role and policy for the Firehose stream.
- Deployment of an EventBridge rule to capture GuardDuty findings as reported by Security Hub.
- Configuration of the Kinesis Data Firehose to relay data to a specified Splunk endpoint.
- Integration of GuardDuty with the Kinesis stream via EventBridge.

# Usage
The script can be ran with the following:
```
python kinesis_guardduty_deployment.py -profile <insert profile> -region <insert region> -account_id <insert account id>
```
Please note that the initializing the script will result in two additional bits of information via a user input prompt (see below). Both of these items should be provided to you by the Splunk team. They are required for successfully deployment.
- HEC Token
- HTTP Endpoint URL

A test Guard Duty finding can be generated from within AWS with the following (AWS CLI):
```
aws guardduty create-sample-findings --detector-id <insert detector id> --finding-types Backdoor:EC2/DenialOfService.Tcp
```

Although in the example above the "Backdoor:EC2/DenialOfService.Tcp" finding type was utilized, a full listing of available Guard Duty finding types can be found here [Finding Types - Amazon GuardDuty](https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_finding-types-active.html)

# Targets
This script should only be ran in the following locations:
- The AWS account that has been designated as the delegated administrator account for Guard Duty and/or Security Hub. This account will ingest all Guard Duty findings, regardless of severity, for all member accounts, in all regions. By leveraging the aggregation capabilities of Security Hub in the delegated administrator account, findings from all regions and accounts will be successfully reported.
- A single AWS account that has been designated for testing. Once testing is complete, please delete deployed resources.

# Considerations
- Guard Duty is a regional service. For each region in which there are resources, Guard Duty must be enabled and an account must be designated as the delegated administrator account for that region. The delegated administrator account cannot be the master account. It is best to have all regions share the same AWS account ID for the sake of simplicity and centralization.
- Security Hub is also a regional service, but offers aggregation capabilities. When configured correctly, all Guard Duty findings from all regions and/or accounts will be aggregated and reported in the delegated administrator account and region via Security Hub.
- Guard Duty deployment is a prerequisite for deployment. This script must be ran in each region for which Guard Duty is deployed. However, simply change the applicable region, account id, and profile information to utilize this script for deploymnent in those regions. 
