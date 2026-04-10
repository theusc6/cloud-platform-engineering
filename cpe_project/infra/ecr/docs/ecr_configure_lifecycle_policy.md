# Configuring Elastic Container Registry (ECR) Repository Lifecycle Policies

## Overview
This script will set the ECR repository lifecycle policy to expire all images except for the (5) most recent. 

## Actions
This script will perform the following actions:
- Set the ECR repository lifecycle policy to expire "imageCountMoreThan" to (5).

## Usage
This script can be ran with the below command:

```
python ecr_configure_lifecycle_policy.py --profile <insert_profile> --repository <insert_repository_name> --region <inset_region>
```

## Targets
This script is designed to target AWS Accounts with ECR repositories that either fail to comply with baseline lifecycle policy requirements or lack a lifecycle policy configuration altogether.

## Considerations
- The "imageCountMoreThan" setting can be modified to meet specific requirements for your environment. This setting will configure the value to the maximum number of images that you want to retain in your repository. (0) is not configurable.
- You may also use "sinceImagePushed", which will set the value to the maximum age limit for your images. (0) is not configurable. Please be aware that if all images are older than the configured number of days, all images meeting this requirement will be deleted. It may be best to utilize "imageCountMoreThan" if a certain number of images should be retained, regardless of age.
