# Enabling Automatic Minor Version Upgrades for an RDS Database Instance

## Overview
This script enables Automatic Minor Version Upgrades for an RDS Database Instance.

## Actions
This script takes the following actions:
- Enables Automatic Minor Version Upgrades for an RDS Database Instance
- Applies the update immediately

## Usage
The script can be ran with the following command:

```
python rds_enable_minor_version_upgrades.py --profile <insert profile> --region <insert region> --dbinstance <database instance name>
```

## Target(s)
This script should be ran in any AWS account that contains a non-compliant RDS Database instance.

## Considerations
- See link here for in-depth description of actions to enable Automatic Minor Version Upgrades: [Upgrading a DB instance engine version](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.Upgrading.html#USER_UpgradeDBInstance.Upgrading.AutoMinorVersionUpgrades)
- Due to the script applying the update immediately, there may be temporary downtime of the instance as a result. You can either modify the script to apply the update at a later date/time or schedule the change during a maintenance window.
