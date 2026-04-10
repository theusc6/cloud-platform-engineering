# Enabling Deletion Protection on a DynamoDB Table

## Overview
This script enables deletion protection for a DynamoDB Table. 

## Actions
This script takes the following actions:
- Enables deletion protection for specified DynamoDB table.

## Usage
The script can be ran with the following command:

```
python dynamodb_enable_deletion_protection.py --profile <insert profile> --region <insert region> --tablename <dynamodb table name>
```

## Target(s)
This script should be ran in any AWS account that contains a DynamoDB table that does not have deletion protection enabled.

## Considerations
- See link here for in-depth description of enabling deletion protection for a DynamoDB Table: [Using deletion protection to protect your table](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-deletion-protection.html)
