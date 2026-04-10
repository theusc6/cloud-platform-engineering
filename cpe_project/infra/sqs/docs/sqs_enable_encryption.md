# Enabling Encryption for a SQS Queue

## Overview
This script enables encryption on an SQS Queue.

## Actions
This script takes the following actions:
- Enables encryption for an SQS Queue

## Usage
The script can be ran with the following command:

```
python sqs_enable_encryption.py --profile <insert profile> --region <insert region> --queue <sqs queue name>
```

## Target(s)
This script should be ran in any AWS account that contains an unencrypted SQS queue.

## Considerations
- See link here for in-depth description of encrypting an SQS queue: [Encryption at Rest - Amazon Simple Queue Service (SQS)](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-server-side-encryption.html)
- This script will configure encryption to utilize SSE-KMS. AWS KMS combines secure, highly available hardware and software to provide a key management system scaled for the cloud. When you use Amazon SQS with AWS KMS, the data keys that encrypt your message data are also encrypted and stored with the data they protect.
- The following are benefits of using AWS KMS:
  - You can create and manage AWS KMS keys yourself.
  - You can also use the AWS managed KMS key for Amazon SQS, which is unique for each account and region.
  - The AWS KMS security standards can help you meet encryption-related compliance requirements.
