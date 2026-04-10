# Enabling CloudWatch Logging for an RDS Database Instance

## Overview
This script enables CloudWatch Logging for an RDS Database Instance.

## Actions
This script takes the following actions:
- Enables CloudWatch Logging for an RDS Database Instance
  - The default Log Types to be enabled are: Error, Audit, General, & Slow Query
- Applies the update immediately

## Usage
The script can be ran with the following command:

```
python rds_configure_cloudwatch_logging.py --profile <insert profile> --region <insert region> --dbinstance <database instance name>
```

## Target(s)
This script should be ran in any AWS account that contains a non-compliant RDS Database instance.

## Considerations
- See link here for in-depth description of actions to enable CloudWatch Logging: [Publishing MySQL logs to Amazon CloudWatch Logs](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_LogAccess.MySQLDB.PublishtoCloudWatchLogs.html)
- Modifying CloudWatch Logging (and the logging types) always applies immediately, there may be temporary downtime of the instance as a result. Performing this change during a maintenance window may be required.
- Each DB type (MariaDB, MySQL, etc.) will support different logging types, which can also be determined by version as well. This may require modification of the script depending on the target DB type. The current script is written to demonstrate how it will be applied to (and can be modified) for **MySQL**. You can find the latest documentation from AWS on this topic here: [Deciding which logs to publish to CloudWatch Logs](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_LogAccess.Procedural.UploadtoCloudWatch.html#engine-specific-logs)
