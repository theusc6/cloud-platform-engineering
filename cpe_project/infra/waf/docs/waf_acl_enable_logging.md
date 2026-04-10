# Enable Web Application Firewall (WAF) Logging

## Overview
This script will enable logging of a Web Application Firewall (WAF) Access Control List (ACL). The logging destination will be a security-compliant S3 bucket.

## Actions
This script will perform the following actions:
- Create a fully compliant S3 Bucket for the log destination
- Enable WAF ACL logging on either a single WAF ACL or all WAF ACL(s) in the target account

## Usage
The script can be ran with the below command:

```
python waf_acl_enable_logging.py --profile <insert profile> --region <insert region> --waf_acl <insert waf acl id>
```

## Target(s)
This script should be ran in any AWS account that contains WAF ACL(s) that do not currently have logging enabled.

## Considerations
- Although S3 Buckets do not have to be log destination, that is what is configured here. There is also an option to use CloudWatch Logs if desired.
- The `-a` flag can be used to enable logging for all WAF ACL(s) in the target account
