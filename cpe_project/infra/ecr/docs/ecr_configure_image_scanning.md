# Configuring Elastic Container Registry (ECR) Private Repository Image Scanning

## Overview
This script will configure private ECR repositories to use enhanced scanning (i.e. continuous) with a wildcard filter.

## Actions
This script will perform the following actions:
- Configure the ECR repository to utilize continuous, enhanced scanning with a wildcard filter (scan all images/private repositories). 

## Usage
This script can be ran with the below command:

```
python ecr_configure_image_scanning.py --profile <insert_profile> --region <inset_region>
```

## Targets
This script is designed to target AWS Accounts with ECR repositories that either fail to comply with baseline ECR scanning requirements or lack image/repository scanning altogether.

## Considerations
- A filter with a wildcard (*) matches on any repository name where the wildcard replaces zero or more characters in the repository name.
- Enhanced scanning: Amazon ECR integrates with Amazon Inspector to provide automated, continuous scanning of your repositories. Your container images are scanned for both operating systems and programing language package vulnerabilities. As new vulnerabilities appear, the scan results are updated and Amazon Inspector emits an event to EventBridge to notify you.
- When enhanced scanning is used, you may specify separate filters for scan on push and continuous scanning. Any repositories not matching an enhanced scanning filter will have scanning disabled. If you are using enhanced scanning and specify separate filters for scan on push and continuous scanning where multiple filters match the same repository, then Amazon ECR enforces the continuous scanning filter over the scan on push filter for that repository.
