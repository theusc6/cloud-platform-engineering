# Enabling Encryption for a Kinesis Stream

## Overview
This script enables encryption on a Kinesis Stream. 

## Actions
This script takes the following actions:
- Enables encryption for a Kinesis Stream

## Usage
The script can be ran with the following command:

```
python kinesis_enable_encryption.py --profile <insert profile> --region <insert region> --stream <kinesis stream name>
```

## Target(s)
This script should be ran in any AWS account that contains an unencrypted Kinesis Stream.

## Considerations
- See link here for in-depth description of encrypting a Kinesis Stream: [What Is Server-Side Encryption for Kinesis Data Streams?](https://docs.aws.amazon.com/streams/latest/dev/what-is-sse.html)
- This script will set the KMS key to be the AWS managed CMK, ```alias/aws/kinesis```. If a Customer Managed Key is preferred, the script will need to be modified and a KMS ARN will need to be provided. 
