# IAM Role & Policy Query Usage

## Overview
This script will query for IAM role & policy information in a given account when provided with a keyword. The query will return all roles (and their policies) that contain the keyword. 

## Actions
This script takes the following actions:
- Queries for roles and their attached policies based on the provided keyword
- Exports this information to an Excel document. This documents contains the following information:
  - Role Name
  - Attached Policy Name
  - Policy Type (AWS Managed or Customer Managed)
  - Full permissions associated with policy
  - When the role was last used (if ever)

## Usage
The script can be ran with the following command:

```
python iam_role_and_policy_query.py --profile <insert profile> --keyword <insert keyword>
```

## Target(s)
This script can be executed in any AWS account to query roles by keyword.

## Considerations
- Please note that IAM is a global service, thus region does not have to be specified.
- IAM is different than IAM Identity Center, thus this script will not return permission sets.
- This script will output the XLSX file in the location from which the script is ran.
