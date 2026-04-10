# EBS Snapshot Removal Tool

## Overview
This tool will delete EBS snapshots based on the provided tag name/value combination.

## Actions
This script takes the following actions:
- Checks for EBS snapshots that have the matching tag name & value
- Validates the snapshot is not in use and/or it does not have any other disqualifying characteristics
- Delete specified snapshots as determined by tag name/value combination

## Usage
The script can be ran with the following command:

```
python ebs_snapshot_removal.py --profile <insert profile> --region <insert region> --tag <insert tag name> --value <insert tag value>
```

## Target(s)
This script should be ran in any AWS account that contains EBS snapshots that are outdated, uneeded, or unused. This script should be used in conjunction with the EBS Lifecycle Manager, with implementation of Data Lifecycle Policies.

## Considerations
- This script deletes snapshots, which is a destructive operation. Ensure to verifythe tag key and value parameters to avoid accidental deletion of unintended snapshots.
