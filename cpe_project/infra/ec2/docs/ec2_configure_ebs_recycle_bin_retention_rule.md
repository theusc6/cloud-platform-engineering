# Configuring EBS Recycle Bin Retention Rules

## Overview
This script configured an EBS recycle bin retention rule that helps to retain deleted snapshots for a specified period of time. 

## Actions
This script takes the following actions:
- Creates an EBS Recycle Bin Retention Rule

## Usage
The script can be ran with the following command:

```
python ec2_configure_ebs_recycle_bin_retention_rule.py --profile <insert profile> --region <insert region> --rulename <rule name> --retention <number of days to retain>
```

## Target(s)
This script should be ran in any AWS account that requires a retention rule for the EBS recycle bin.

## Considerations
- This script can be modified to handle AMI deletion as well. Note, the number of days to retain is fully configurable. The MyOrg-default is (14) days, but that can be extended as needed. 
