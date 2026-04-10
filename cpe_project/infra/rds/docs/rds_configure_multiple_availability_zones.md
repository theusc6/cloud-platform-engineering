# Enabling Multi-AZ for an RDS Database Instance

## Overview
This script enables Multi-AZ for an RDS Database Instance.

## Actions
This script takes the following actions:
- Enables Multi-AZ for an RDS Database Instance
- Applies the update immediately

## Usage
The script can be ran with the following command:

```
python rds_configure_multiple_availability_zones.py --profile <insert profile> --region <insert region> --dbinstance <database instance name>
```

## Target(s)
This script should be ran in any AWS account that contains a non-compliant RDS Database instance.

## Considerations
- See link here for in-depth description of actions to enable Multi-AZ: [Configuring and managing a Multi-AZ deployment](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.html)
- Due to the script applying the update immediately, there may be temporary downtime of the instance as a result. You can either modify the script to apply the update at a later date/time or schedule the change during a maintenance window. *Note: This modifcation takes significantly longer than many other types of changes. Keep this in mind when running this script outside of a pre-defined maintenance window.*
