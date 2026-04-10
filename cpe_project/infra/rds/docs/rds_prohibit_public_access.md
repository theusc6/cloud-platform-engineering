# Prohibiting Public Access to an RDS Instance

## Overview
This script prohibits public access to an RDS Instance.

## Actions
This script takes the following actions:
- Marks the RDS Instance as "Publicly Accessible = False", thus prohibiting any public access.
- Applies the update immediately

## Usage
The script can be ran with the following command:

```
python rds_prohibit_public_access.py --profile <insert profile> --region <insert region> --dbinstance <database instance name>
```

## Target(s)
This script should be ran in any AWS account that contains a non-compliant RDS Database instance.

## Considerations
- See link here for in-depth description of RDS Controls: [Amazon Relational Database Service controls](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html)
- Modifying Public Access settings always applies immediately, there may be temporary downtime of the instance as a result. Performing this change during a maintenance window may be required.
