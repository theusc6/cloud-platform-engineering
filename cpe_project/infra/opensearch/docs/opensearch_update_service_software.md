# Updating Opensearch Domain Service Software

## Overview
This script updates the service software for an Opensearch domain

## Actions
This script takes the following actions:
- Intakes user input to define the update schedule, either NOW or OFF_PEAK_WINDOW
- Updates the service software

## Usage
The script can be ran with the following command:

```
python opensearch_update_service_Software.py --profile <profile_name> --domain <domain_name>
```

## Target(s)
This script should be ran in any AWS account that contains an Opensearch domain that is flagged as being out of date.

## Considerations
- Manually updating your domain lets you take advantage of new features more quickly. When you choose Update, OpenSearch Service places the request in a queue and begins the update when it has time.
- When you initiate a service software update, OpenSearch Service sends a notification when the update starts and when it completes.
- Software updates use blue/green deployments to minimize downtime. Updates can temporarily strain a cluster's dedicated master nodes, so make sure to maintain sufficient capacity to handle the associated overhead.
- Updates typically complete within minutes, but can also take several hours or even days if your system is experiencing heavy load. Consider updating your domain during the configured off-peak window to avoid long update periods.
