# Disabling IMDSv1

## Overview
This script disables IMDSv1 on the target EC2 instance, complying with Security Hub control [EC2.8]. This control checks whether your Amazon Elastic Compute Cloud (Amazon EC2) instance metadata version is configured with Instance Metadata Service Version 2 (IMDSv2). The control passes if HttpTokens is set to required for IMDSv2. The control fails if HttpTokens is set to optional.

## Actions
This script takes the following actions:
- Disables IMDSv1, requires use of IMDSv2

## Usage
The script can be ran with the following command:

```
python ec2_disable_imdsv1.py --profile <insert profile> --region <insert region> --instance <insert instance id>
```

## Target(s)
This script should be ran in any AWS account that contains a non-compliant Ec2 instance running IMDSv1.

## Considerations
- Please see [Recommended Path to Requiring IMDSv2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-metadata-transition-to-version-2.html#recommended-path-for-requiring-imdsv2) for a detailed breakdown on checks to be performed priore to making this change.
- When the CloudWatch metric MetadataNoToken records zero IMDSv1 usage, your instances are ready to be fully transitioned to using IMDSv2.
