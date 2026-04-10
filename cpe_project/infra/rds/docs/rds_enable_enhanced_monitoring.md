# Enabling Enhanced Monitoring for RDS Database Instance

## Overview
This script enables Enhanced Monitoring for an RDS Database Instance.

## Actions
This script takes the following actions:
- Creates the enhanced monitoring policy
- Creates the enhanced monitoring role
- Attaches the above policy to the above role
- Creates CloudWatch Log Group
- Creates CloudWatch Log Stream
- Enables Enhanced Monitoring on the specified RDS DB
- Applies the update immediately

## Usage
The script can be ran with the following command:

```
python rds_enable_enhanced_monitoring.py --profile <insert profile> --region <insert region> --dbinstance <database instance name> --interval <monitoring interval in seconds>
```

## Target(s)
This script should be ran in any AWS account that contains a non-compliant RDS Database instance.

## Considerations
- See link here for in-depth description of actions to enable Enhanced Monitoring: [Overview of Enhanced Monitoring](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_Monitoring.OS.overview.html)
- Due to the script applying the update immediately, there may be temporary downtime of the instance as a result. You can either modify the script to apply the update at a later date/time or schedule the change during a maintenance window.
