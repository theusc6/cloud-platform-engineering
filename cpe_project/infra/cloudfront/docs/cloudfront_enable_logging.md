# Enable Logging for CloudFront Distributions

## Overview
This script enables logging to an S3 bucket for CloudFront distributions

## Actions
This script takes the following actions:
- Enables logging to a target S3 Bucket for CloudFront distributions
- Creates fully compliant target S3 Bucket (if one does not already exist in account)

## Usage
The script can be ran with the following command:

```
python3 cloudfront_enable_logging.py --profile <insert profile> --region <insert region> --distribution <insert distribution id>
```

## Target(s)
This script should be ran in any AWS account that contains a CloudFront distribution that does not have logging enabled.

## Considerations
- The target S3 bucket must have ACLs enabled. 
