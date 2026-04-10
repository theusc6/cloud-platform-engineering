# Overview
This script will enable auto rotation for a KMS key

## Action
- Enable auto rotation for specified KMS key

## Usage
The script can be initiated by the following:

```
python kms_enable_auto_rotation.py --region <insert region> --profile <insert profile> -- key <insert key id>
```

## Target(s)
This script can be used in any account and for any KMS key that does not have auto rotation enabled. 

## Considerations
- The properties of the KMS key, including its key ID, key ARN, region, policies, and permissions, do not change when the key is rotated
- You do not need to change applications or aliases that refer to the key ID or key ARN of the KMS key
- Rotating key material does not affect the use of the KMS key in any AWS service
- After you enable key rotation, AWS KMS rotates the KMS key automatically every year. You don't need to remember or schedule the update
