# Configuring Elastic Container Registry (ECR) Repository Tag Immutability

## Overview
This script will configure the ECR repository to enable tag immutability.

## Actions
This script will perform the following actions:
- Enable tag immutability on the target repository. 

## Usage
This script can be ran with the below command:

```
python ecr_configure_tag_immutability.py --profile <insert_profile> --repository <insert_repository_name> --region <inset_region>
```

## Targets
This script is designed to target AWS Accounts with ECR repositories that either fail to comply with baseline configuration requirements or lack tag immutability altogether.

## Considerations
- Each repository will need to have tag immutability configured.
