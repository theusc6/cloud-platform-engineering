# Enabling Default Ec2 Encryption

## Overview
This script enables an AWS account to enforce the encryption of the new EBS volumes and snapshot copies that you create.

## Actions
This script takes the following actions:
- Enables default EBS encryption for the specific account and region

## Usage
The script can be ran with the following command:

```
python ec2_enable_ebs_default_encryption.py --profile <insert profile> --region <insert region>
```

## Target(s)
This script should be ran in any AWS account that does not have default Ec2/EBS encryption enabled by default.

## Considerations
- Encryption by default has no effect on existing EBS volumes or snapshots.
- Encryption by default is a Region-specific setting. If you enable it for a Region, you cannot disable it for individual volumes or snapshots in that Region. Additionally, this script must be ran in each region individually.
- Amazon EBS encryption by default is supported on all current generation and previous generation instance types.
- If you copy a snapshot and encrypt it to a new KMS key, a complete (non-incremental) copy is created. This results in additional storage costs.
- When migrating servers using AWS Server Migration Service (SMS), do not turn on encryption by default. If encryption by default is already on and you are experiencing delta replication failures, turn off encryption by default. Instead, enable AMI encryption when you create the replication job.
