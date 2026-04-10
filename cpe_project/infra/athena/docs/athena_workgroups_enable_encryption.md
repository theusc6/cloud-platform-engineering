# Enable Encrpytion for Athena Workgroups

## Overview
This script enables encrpytion (default Amazon S3-managed keys (SSE_S3) for a specified Athena Workgroup

## Actions
This script takes the following actions:
- Enables SSE_S3 encryption for the provided Athena Workgroup

## Usage
The script can be ran with the following command:

```
python athena_workgroups_enable_encryption.py --profile <insert profile> --region <insert region> --workgroup <insert workgroup name>
```

## Target(s)
This script should be ran in any AWS account that contains an Athena Workgroup that is not encrypted in any way.

## Considerations
- Although SSE_S3 is used in this script (and is the default) you may also encrypt workgroups with either KMS-managed keys (SSE_KMS) or client-side encryption with KMS-managed keys (CSE_KMS). In either case, additional resources may need to be provisioned for the encryption method to succeed.
