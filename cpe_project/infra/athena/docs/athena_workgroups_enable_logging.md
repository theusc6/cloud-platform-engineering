# Enable Logging for Athena Workgroups

## Overview
This script enables logging for a specified Athena Workgroup

## Actions
This script takes the following actions:
- Enables cloudwatch logging for the provided Athena Workgroup

## Usage
The script can be ran with the following command:

```
python athena_workgroups_enable_logging.py --profile <insert profile> --region <insert region> --workgroup <insert workgroup name>
```

## Target(s)
This script should be ran in any AWS account that contains an Athena Workgroup that is not configured to log.

## Considerations
- Note that the "Regions" argument can take a list of comma separated regions, this is helpful when running the script against the same Workgroup in multiple regions.