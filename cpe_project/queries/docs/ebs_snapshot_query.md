# EBS Snapshot Query

## Overview
This script will query for all EBS Snapshots in a given account and region. Snapshots will be exported to an Excel document.

## Actions
This script takes the following actions:
- Queries for all EBS Snapshots in a given account & region
- The following data will be collected for each snapshot:
  - Snapshot ID
    - The snapshot ID.
  - Volume ID
    - The ID of the volume the snapshot is for.
  - State
    - The snapshot state.
  - Start Time
    -  The time stamp when the snapshot was initiated.
  - Volume Size
    - The size of the volume, in GiB.
  - Name
    - Extracted from Tag key "Name", if exists
  - Description
    - The description for the snapshot.
  - Storage Tier
    - The storage tier in which the snapshot is stored. standard indicates that the snapshot is stored in the standard snapshot storage tier and that it is ready for use. archive indicates that the snapshot is currently archived and that it must be restored before it can be used.
  - Volume Type
    - Type of volume the snapshot is from
  - Owner
    - The ID of the Amazon Web Services account that owns the EBS snapshot.
  - Encryption Status
    - Indicates whether the snapshot is encrypted.
- The above data wil be exported to an Excel document named "ebs_snapshot_query_{Account ID}_{Current Date}.xlsx"

## Usage
The script can be ran with the following command:

```
python ebs_snapshot_query.py --profile <insert profile> --region <insert region>
```

## Target(s)
This script can be executed in any AWS account in which an EBS report should be generated.

## Considerations
- Please note that EC2 is a regional service, and to generate a report for all snapshots, (1) execution is required per region. 
