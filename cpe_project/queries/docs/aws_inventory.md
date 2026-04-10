# AWS Inventory Script

## Overview
This script performs a full AWS infrastructure inventory for select resources across all accounts in an AWS Organization (or a selected environment such as dev/prod/uat). It collects metadata from dozens of AWS services, aggregates results into a single Excel workbook, and uses caching + concurrency for optimal speed.

The script is read-only:
It does not modify any AWS resources and uses only list and describe API calls.

## Services Scanned
Below is the complete list of services, the key metadata collected for each, and the corresponding cache file that accelerates future runs.

| AWS Service | Metadata Collected | Cache File |
|------------|--------------------|------------|
| **ECS** | Clusters, services, tasks, tags | `ecs_cache.json` |
| **EC2** | Instances, IPs, AZ, platform, tags | `ec2_cache.json` |
| **EBS** | Volumes, state, size, type, attachments | `ebs_cache.json` |
| **RDS** | Instances, engine, class, storage, tags | `rds_cache.json` |
| **Lambda** | Functions, runtimes, sizes, tags | `lambda_cache.json` |
| **ECR** | Repos, image counts, sizes | `ecr_cache.json` |
| **S3** | Region, size, object count, encryption, public access | `s3_cache.json` |
| **CloudWatch** | Metrics, namespaces, alarms, logs, retention, cost | `cloudwatch_cache.json` |
| **VPC** | VPC ID, subnets, routes, IGW/NAT count, flow logs | `vpc_cache.json` |
| **SecurityHub** | Standards enabled, findings count, cost | `securityhub_cache.json` |
| **GuardDuty** | Detectors, status, findings | `guardduty_cache.json` |
| **Inspector (Inspector2)** | Findings, templates, cost | `inspector_cache.json` |
| **Macie** | Buckets monitored, findings count | `macie_cache.json` |
| **Config** | Recorders, rules, non-compliant counts | `config_cache.json` |
| **IAM** | Users, roles, MFA, tags | `iam_cache.json` |
| **KMS** | Keys, state, rotation, manager, tags | `kms_cache.json` |
| **DynamoDB** | Tables, item count, size, throughput | `dynamodb_cache.json` |
| **Glue** | Jobs, state, last run, tags | `glue_cache.json` |
| **DataSync** | Tasks, source/destination, bytes transferred | `datasync_cache.json` |
| **Kinesis** | Streams, shard count, retention, status | `kinesis_cache.json` |
| **ELB (ALB/NLB/CLB)** | Name, DNS, scheme, target groups, tags | `elb_cache.json` |
| **Route 53** | Hosted zones, record counts, tags | `route53_cache.json` |
| **WAF** | Web ACLs, metrics, rule count | `waf_cache.json` |
| **API Gateway** | APIs, protocol, endpoint, tags | `apigateway_cache.json` |
| **AppSync** | APIs, auth type, tags | `appsync_cache.json` |
| **SageMaker** | Notebooks, instance types, statuses | `sagemaker_cache.json` |
| **FSx** | Filesystems, type, size, state, tags | `fsx_cache.json` |
| **WorkSpaces** | Workspace details, bundles, users, state, tags | `workspaces_cache.json` |
| **Backup** | Vaults, recovery point count, total size | `backup_cache.json` |
| **Direct Connect** | Connections, bandwidth, locations, state | `directconnect_cache.json` |
| **Step Functions** | State machines, definition size, tags | `stepfunctions_cache.json` |
| **Lightsail** | Instances, blueprints, bundles, state, tags | `lightsail_cache.json` |
| **CloudTrail** | Trail configuration, validation, S3 logging | `cloudtrail_cache.json` |

## Usage
The script can be ran with the following command:

```
python3 aws_inventory.py -p <aws-profile> -e <env>
```

Please select between "dev", "uat", or "prod" environments as needed.

## Output(s)
All resources export into:
```
AWS_Inventory_Report-AllRegions.xlsx
```

# Considerations
- If new resources need to be added in the future, please add the appropriate blocks for cache, function(s), and a place for the excel data. This is all that is needed to expand the query to new resources. 
- Always first test on the development environment when adding new features to this script. 