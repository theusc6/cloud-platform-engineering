# Enabling DocumentDB Audit Logging

## Overview
This script enablese DocumentDB Audit Logging to AWS CloudWatch.

## Actions
This script takes the following actions:
- Enables CloudWatch Audit logging on the DocumentDB cluster.

## Usage
The script can be ran with the following command:

```
python documentdb_enable_audit_logging.py --profile <insert profile> --region <insert region> --cluster-identifier <cluster identifier>
```

## Target(s)
This script should be ran in any AWS account that contains a non-compliant DocumentDB cluster.

## Considerations
- See link here for in-depth description of actions to enable audit logging [Auditing Amazon DocumentDB Events](https://docs.aws.amazon.com/documentdb/latest/developerguide/event-auditing.html#event-auditing-enabling-auditing)
