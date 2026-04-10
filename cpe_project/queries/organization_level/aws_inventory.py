"""
us_ecs_query.py
Enhanced AWS ECS & EC2 inventory script with:

- Environment selection (dev/prod/uat/all)
- Concurrency for faster scans
- Progress bars (tqdm)
- Caching for ECS and EC2 queries
- Single Excel output with two sheets:
    1. Cluster Details (ECS)
    2. EC2 Details

This script is READ-ONLY. It performs only list/describe calls to AWS services
and writes results locally to Excel. It makes no changes to AWS resources.

"""

import json
import os
import argparse
from datetime import datetime, UTC, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import boto3
import pandas as pd
from botocore.exceptions import ClientError, EndpointConnectionError
from tqdm import tqdm

def strip_timezone(df):
    """
    Converts timezone-aware datetime columns to naive datetime
    so Excel can handle them without crashing.
    """
    for col in df.columns:
        if "datetime64" in str(df[col].dtype):
            try:
                df[col] = df[col].dt.tz_localize(None)
            except Exception:
                pass
    return df


# Cache files
ECS_CACHE_FILE = "ecs_cache.json"
EC2_CACHE_FILE = "ec2_cache.json"
EBS_CACHE_FILE = "ebs_cache.json"
RDS_CACHE_FILE = "rds_cache.json"
LAMBDA_CACHE_FILE = "lambda_cache.json"
ECR_CACHE_FILE = "ecr_cache.json"
S3_CACHE_FILE = "s3_cache.json"
CLOUDWATCH_CACHE_FILE = "cloudwatch_cache.json"
VPC_CACHE_FILE = "vpc_cache.json"
SECURITYHUB_CACHE_FILE = "securityhub_cache.json"
GUARDDUTY_CACHE_FILE = "guardduty_cache.json"
INSPECTOR_CACHE_FILE = "inspector_cache.json"
MACIE_CACHE_FILE = "macie_cache.json"
CONFIG_CACHE_FILE = "config_cache.json"
IAM_CACHE_FILE = "iam_cache.json"
KMS_CACHE_FILE = "kms_cache.json"
DYNAMODB_CACHE_FILE = "dynamodb_cache.json"
GLUE_CACHE_FILE = "glue_cache.json"
DATASYNC_CACHE_FILE = "datasync_cache.json"
KINESIS_CACHE_FILE = "kinesis_cache.json"
ELB_CACHE_FILE = "elb_cache.json"
ROUTE53_CACHE_FILE = "route53_cache.json"
WAF_CACHE_FILE = "waf_cache.json"
APIGW_CACHE_FILE = "apigateway_cache.json"
APPSYNC_CACHE_FILE = "appsync_cache.json"
SAGEMAKER_CACHE_FILE = "sagemaker_cache.json"
FSX_CACHE_FILE = "fsx_cache.json"
WORKSPACES_CACHE_FILE = "workspaces_cache.json"
BACKUP_CACHE_FILE = "backup_cache.json"
DIRECTCONNECT_CACHE_FILE = "directconnect_cache.json"
STEPFUNCTIONS_CACHE_FILE = "stepfunctions_cache.json"
LIGHTSAIL_CACHE_FILE = "lightsail_cache.json"
CLOUDTRAIL_CACHE_FILE = "cloudtrail_cache.json"









CACHE_TTL_HOURS = 24

# Account sets ----------------------------------------------------------

# Production accounts
PROD_ACCOUNTS = [
    "123456789012",  # myorg-4cs-prod
    "123456789012",  # myorg-apis-prod
    "123456789012",  # myorg-css-prod
    "123456789012",  # myorg-dig-prod
    "123456789012",  # myorg-facetware-prod
    "123456789012",  # myorg-global-everest-prod
    "123456789012",  # myorg-global-ge-applications-prod
    "123456789012",  # myorg-global-grading-engine-prod
    "123456789012",  # myorg-hk-infra-prod
    "123456789012",  # myorg-app-prod
    "123456789012",  # myorg-labdocs-prod
    "123456789012",  # myorg-labspark-prod
    "123456789012",  # myorg-mpp-prod
    "123456789012",  # myorg-nms-prod
    "123456789012",  # myorg-omd-prod
    "123456789012",  # myorg-sample-app-1-prod
    "123456789012",  # myorg-rds-prod
    "123456789012",  # myorg-sample-app-2-prod
    "123456789012",  # myorg-static-websites-prod
    "123456789012",  # myorg-warp-prod
    "123456789012",  # myorg-wireframe-matching-prod
    "123456789012",  # Log Archive
    "123456789012",  # Security Tooling
    "123456789012",  # myorg-iam
    "123456789012",  # myorg-master
    "123456789012",  # Audit
    "123456789012",  # devops
    "123456789012",  # MyOrg WebServers
    "123456789012",  # MyOrg-ReportResults-DataLake
    "123456789012",  # myorg-security
    "123456789012",  # myorg-shared-services
    "123456789012",  # myorg-ai-training
    "123456789012",  # MyOrg-DataSci
    "123456789012",  # myorg-drives
    "123456789012",  # MyOrg-Network
]

# Development accounts
DEV_ACCOUNTS = [
    "123456789012",  # myorg-4cs-dev
    "123456789012",  # myorg-agd-dev
    "123456789012",  # myorg-apis-dev
    "123456789012",  # myorg-css-dev
    "123456789012",  # myorg-dig-dev
    "123456789012",  # myorg-everest-dev
    "123456789012",  # myorg-facetware-dev
    "123456789012",  # myorg-global-ge-applications-dev
    "123456789012",  # myorg-grading-engine-dev
    "123456789012",  # myorg-iam-dev
    "123456789012",  # myorg-app-dev
    "123456789012",  # myorg-labdocs-dev
    "123456789012",  # myorg-labspark-dev
    "123456789012",  # myorg-mpp-dev
    "123456789012",  # myorg-nms-dev
    "123456789012",  # myorg-sample-app-1-dev
    "123456789012",  # myorg-rds-dev
    "123456789012",  # myorg-sample-app-2-dev
    "123456789012",  # myorg-static-websites-dev
    "123456789012",  # myorg-verifier-dev
    "123456789012",  # myorg-warp-dev
    "123456789012",  # myorg-wireframe-matching-dev
    "123456789012",  # myorg-training
]

# UAT accounts
UAT_ACCOUNTS = [
    "123456789012",  # myorg-4cs-uat
    "123456789012",  # myorg-dig-uat
    "123456789012",  # myorg-facetware-uat
    "123456789012",  # myorg-iam-uat
    "123456789012",  # myorg-app-uat
    "123456789012",  # myorg-mpp-uat
    "123456789012",  # myorg-nms-uat
    "123456789012",  # myorg-sample-app-1-uat
    "123456789012",  # myorg-sample-app-2-uat
    "123456789012",  # myorg-warp-uat
    "123456789012",  # myorg-rds-test
    "123456789012",  # myorg-aws-grading-engine-shared
    "123456789012",  # myorg-global-everest-shared
    "123456789012",  # myorg-global-everest-stage
    "123456789012",  # myorg-mpp-shared
]

# ----------------------------------------------------------------------
# Cache Utilities
# ----------------------------------------------------------------------

def load_cache(file_path):
    """Load a JSON cache file if it exists; skip invalid/corrupt files."""
    if os.path.exists(file_path):
        try:
            with open(file_path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError, ValueError):
            print(f"Cache file {file_path} is invalid or corrupt — ignoring and rebuilding.")
            return {}
    return {}


def save_cache(file_path, data):
    """Save updated cache to disk."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def is_cache_valid(acct_id, cache_data):
    """Return True if cache entry for acct_id exists and is within TTL."""
    if acct_id not in cache_data:
        return False
    timestamp = datetime.fromisoformat(cache_data[acct_id]["timestamp"])
    return datetime.now() - timestamp < timedelta(hours=CACHE_TTL_HOURS)


# ----------------------------------------------------------------------
# ECS Functions
# ----------------------------------------------------------------------

def get_service_task_definitions(ecs_client, cluster_arn, service_arn):
    """Return task definition details for a given ECS service."""
    try:
        resp = ecs_client.describe_services(
            cluster=cluster_arn,
            services=[service_arn]
        )
        if not resp.get("services"):
            return []

        task_def_arn = resp["services"][0].get("taskDefinition")
        if not task_def_arn:
            return []

        task_resp = ecs_client.describe_task_definition(taskDefinition=task_def_arn)
        task = task_resp.get("taskDefinition", {})

        return [{
            "family": task.get("family"),
            "revision": task.get("revision"),
            "taskDefinitionArn": task.get("taskDefinitionArn"),
            "status": task.get("status"),
            "cpu": task.get("cpu"),
            "memory": task.get("memory"),
            "networkMode": task.get("networkMode"),
            "requiresCompatibilities": task.get("requiresCompatibilities", [])
        }]

    except ClientError:
        return []


def get_cluster_services(ecs_client, cluster_arn):
    """Return list of services running within an ECS cluster."""
    services = []
    try:
        paginator = ecs_client.get_paginator("list_services")
        service_arns = []
        for page in paginator.paginate(cluster=cluster_arn):
            service_arns.extend(page.get("serviceArns", []))

        for i in range(0, len(service_arns), 10):
            resp = ecs_client.describe_services(
                cluster=cluster_arn,
                services=service_arns[i:i+10]
            )
            for svc in resp.get("services", []):
                services.append({
                    "serviceArn": svc.get("serviceArn"),
                    "serviceName": svc.get("serviceName"),
                    "status": svc.get("status"),
                    "desiredCount": svc.get("desiredCount"),
                    "runningCount": svc.get("runningCount"),
                    "pendingCount": svc.get("pendingCount"),
                    "launchType": svc.get("launchType"),
                    "taskDefinition": svc.get("taskDefinition")
                })

    except ClientError:
        return []

    return services


def find_ecs_for_account(account, master_session, regions, ecs_cache):
    """
    Scan ECS clusters for a single AWS account.
    Returns a list of cluster metadata dicts.
    """
    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    # Cache short-circuit
    if is_cache_valid(acct_id, ecs_cache):
        return ecs_cache[acct_id]["data"]

    # Assume role unless master account
    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []
    for region in regions:
        try:
            ecs_client = session.client("ecs", region_name=region)
            cluster_arns = []

            paginator = ecs_client.get_paginator("list_clusters")
            for page in paginator.paginate():
                cluster_arns.extend(page.get("clusterArns", []))

            for i in range(0, len(cluster_arns), 100):
                resp = ecs_client.describe_clusters(
                    clusters=cluster_arns[i:i+100],
                    include=["TAGS"]
                )
                for cluster in resp.get("clusters", []):
                    services = get_cluster_services(ecs_client, cluster["clusterArn"])
                    task_defs = []
                    for svc in services:
                        task_defs.extend(
                            get_service_task_definitions(
                                ecs_client,
                                cluster["clusterArn"],
                                svc["serviceArn"]
                            )
                        )

                    tags = {
                        t["key"]: t.get("value", "")
                        for t in cluster.get("tags", [])
                    }

                    results.append({
                        "Cluster ARN": cluster.get("clusterArn"),
                        "Cluster Name": cluster.get("clusterName"),
                        "Status": cluster.get("status"),
                        "Running Tasks Count": cluster.get("runningTasksCount", 0),
                        "Pending Tasks Count": cluster.get("pendingTasksCount", 0),
                        "Registered Container Instances Count": cluster.get(
                            "registeredContainerInstancesCount", 0
                        ),
                        "Active Services Count": cluster.get("activeServicesCount", 0),
                        "Region": region,
                        "Account ID": acct_id,
                        "Account Name": acct_name,
                        "Environment": acct_env,
                        "Tags": str(tags),
                        "Services": str(services),
                        "Task Definitions": str(task_defs)
                    })
        except ClientError:
            continue

    ecs_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results
    }

    return results


# ----------------------------------------------------------------------
# EC2 Functions
# ----------------------------------------------------------------------

def get_instance_name(instance):
    """Return Name tag if exists, else 'N/A'."""
    if instance.tags:
        for tag in instance.tags:
            if tag["Key"] == "Name":
                return tag["Value"]
    return "N/A"


def find_ec2_for_account(account, master_session, regions, ec2_cache):
    """
    Scan EC2 instances for a single AWS account.
    Returns a list of EC2 instance metadata dicts.
    """
    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    if is_cache_valid(acct_id, ec2_cache):
        return ec2_cache[acct_id]["data"]

    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []

    for region in regions:
        try:
            ec2 = session.resource("ec2", region_name=region)
            for inst in ec2.instances.all():
                state = inst.state["Name"]
                if state not in ("running", "stopped"):
                    continue

                tags = {
                    t["Key"]: t.get("Value", "")
                    for t in inst.tags or []
                }

                results.append({
                    "Instance ID": inst.id,
                    "Name": get_instance_name(inst),
                    "State": state,
                    "Platform": inst.platform or "linux",
                    "Instance Type": inst.instance_type,
                    "Availability Zone": inst.placement.get("AvailabilityZone", "N/A"),
                    "Region": region,
                    "Account ID": acct_id,
                    "Account Name": acct_name,
                    "Environment": acct_env,
                    "Private IP": inst.private_ip_address or "N/A",
                    "Public IP": inst.public_ip_address or "N/A",
                    "Tags": str(tags)
                })
        except ClientError:
            continue

    ec2_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results
    }

    return results

# ----------------------------------------------------------------------
# EBS Functions
# ----------------------------------------------------------------------

def get_volume_name(volume):
    """Return Name tag for EBS volume if present."""
    if volume.tags:
        for tag in volume.tags:
            if tag["Key"] == "Name":
                return tag["Value"]
    return "N/A"


def find_ebs_for_account(account, master_session, regions, ebs_cache):
    """
    Scan EBS volumes for a single AWS account.
    Returns a list of EBS metadata dictionaries.
    """
    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    # Use cache when valid
    if is_cache_valid(acct_id, ebs_cache):
        return ebs_cache[acct_id]["data"]

    # Assume role unless master account
    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []

    for region in regions:
        try:
            ec2 = session.resource("ec2", region_name=region)
            for vol in ec2.volumes.all():
                tags = {t["Key"]: t.get("Value", "") for t in (vol.tags or [])}

                # Attached instances
                attachments = []
                for attach in vol.attachments:
                    attachments.append({
                        "InstanceId": attach.get("InstanceId", "N/A"),
                        "Device": attach.get("Device", "N/A"),
                        "State": attach.get("State", "N/A")
                    })

                results.append({
                    "Volume ID": vol.id,
                    "Name": get_volume_name(vol),
                    "State": vol.state,
                    "Size (GiB)": vol.size,
                    "Volume Type": vol.volume_type,
                    "IOPS": vol.iops if vol.iops else "N/A",
                    "Encrypted": vol.encrypted,
                    "Availability Zone": vol.availability_zone,
                    "Region": region,
                    "Account ID": acct_id,
                    "Account Name": acct_name,
                    "Environment": acct_env,
                    "Attached Instances": str(attachments),
                    "Tags": str(tags),
                })

        except ClientError:
            continue

    # Cache results
    ebs_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results
    }

    return results

# ----------------------------------------------------------------------
# RDS Functions
# ----------------------------------------------------------------------

def get_rds_name(tags):
    """Return Name tag from RDS tag list."""
    if not tags:
        return "N/A"
    for tag in tags:
        if tag.get("Key") == "Name":
            return tag.get("Value", "N/A")
    return "N/A"


def find_rds_for_account(account, master_session, regions, rds_cache):
    """
    Scan RDS DB instances for a single AWS account.
    Returns list of RDS instance metadata dicts.
    """
    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    # Cache short-circuit
    if is_cache_valid(acct_id, rds_cache):
        return rds_cache[acct_id]["data"]

    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []

    for region in regions:
        try:
            rds = session.client("rds", region_name=region)
            paginator = rds.get_paginator("describe_db_instances")

            for page in paginator.paginate():
                for db in page.get("DBInstances", []):
                    arn = db.get("DBInstanceArn")
                    tags_resp = rds.list_tags_for_resource(ResourceName=arn)
                    tags = tags_resp.get("TagList", [])

                    results.append({
                        "DB Instance ID": db.get("DBInstanceIdentifier"),
                        "DB Name": db.get("DBName", "N/A"),
                        "Engine": db.get("Engine"),
                        "Engine Version": db.get("EngineVersion"),
                        "DB Instance Class": db.get("DBInstanceClass"),
                        "Status": db.get("DBInstanceStatus"),
                        "Allocated Storage (GiB)": db.get("AllocatedStorage"),
                        "Storage Type": db.get("StorageType"),
                        "Multi-AZ": db.get("MultiAZ"),
                        "Publicly Accessible": db.get("PubliclyAccessible"),
                        "Region": region,
                        "Availability Zone": db.get("AvailabilityZone", "N/A"),
                        "Endpoint": db.get("Endpoint", {}).get("Address", "N/A"),
                        "Port": db.get("Endpoint", {}).get("Port", "N/A"),
                        "Encrypted": db.get("StorageEncrypted"),
                        "KMS Key": db.get("KmsKeyId", "N/A"),
                        "DB Instance ARN": arn,
                        "Tags": str({t["Key"]: t.get("Value", "") for t in tags}),
                        "Account ID": acct_id,
                        "Account Name": acct_name,
                        "Environment": acct_env,
                    })

        except ClientError:
            continue

    rds_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results
    }

    return results

# ----------------------------------------------------------------------
# Lambda Functions
# ----------------------------------------------------------------------

def find_lambda_for_account(account, master_session, regions, lambda_cache):
    """
    Scan Lambda functions for a single AWS account.
    Returns list of Lambda metadata dicts.
    """
    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    # Use cache if valid
    if is_cache_valid(acct_id, lambda_cache):
        return lambda_cache[acct_id]["data"]

    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []

    for region in regions:
        try:
            lam = session.client("lambda", region_name=region)
            paginator = lam.get_paginator("list_functions")

            for page in paginator.paginate():
                for fn in page.get("Functions", []):
                    fn_arn = fn.get("FunctionArn")

                    # Get tags if possible
                    try:
                        tag_resp = lam.list_tags(Resource=fn_arn)
                        tags = tag_resp.get("Tags", {})
                    except ClientError:
                        tags = {}

                    results.append({
                        "Function Name": fn.get("FunctionName"),
                        "Runtime": fn.get("Runtime", "N/A"),
                        "Handler": fn.get("Handler", "N/A"),
                        "Role": fn.get("Role", "N/A"),
                        "Memory Size": fn.get("MemorySize", "N/A"),
                        "Timeout (sec)": fn.get("Timeout", "N/A"),
                        "Code Size (bytes)": fn.get("CodeSize", "N/A"),
                        "Last Modified": fn.get("LastModified", "N/A"),
                        "State": fn.get("State", "N/A"),
                        "Package Type": fn.get("PackageType", "N/A"),
                        "Architecture": fn.get("Architectures", ["N/A"])[0],
                        "Function ARN": fn_arn,
                        "Region": region,
                        "Account ID": acct_id,
                        "Account Name": acct_name,
                        "Environment": acct_env,
                        "Tags": str(tags)
                    })

        except ClientError:
            continue

    # Cache results
    lambda_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results
    }

    return results

# ----------------------------------------------------------------------
# ECR Functions
# ----------------------------------------------------------------------

def find_ecr_for_account(account, master_session, regions, ecr_cache):
    """
    Scan ECR repositories for a single AWS account.
    Returns a list of repository metadata dictionaries.
    """
    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    # Use cache if valid
    if is_cache_valid(acct_id, ecr_cache):
        return ecr_cache[acct_id]["data"]

    # Assume role if not master
    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []

    for region in regions:
        try:
            ecr = session.client("ecr", region_name=region)
            paginator = ecr.get_paginator("describe_repositories")

            for page in paginator.paginate():
                repos = page.get("repositories", [])
                for repo in repos:
                    repo_name = repo.get("repositoryName")
                    repo_uri = repo.get("repositoryUri")

                    created = repo.get("createdAt")

                    # Strip timezone info so Excel can handle it
                    if created and hasattr(created, "tzinfo") and created.tzinfo is not None:
                        created = created.replace(tzinfo=None)

                    # Attempt to fetch tags
                    try:
                        tag_resp = ecr.list_tags_for_resource(
                            resourceArn=repo.get("repositoryArn")
                        )
                        tags = tag_resp.get("tags", {})
                    except ClientError:
                        tags = {}

                    # Count images
                    try:
                        images = ecr.list_images(
                            repositoryName=repo_name,
                            filter={"tagStatus": "TAGGED"}
                        )
                        image_count = len(images.get("imageIds", []))
                    except ClientError:
                        image_count = "N/A"

                    results.append({
                        "Repository Name": repo_name,
                        "Repository URI": repo_uri,
                        "Image Count": image_count,
                        "Scan On Push": repo.get("imageScanningConfiguration", {}).get("scanOnPush", "N/A"),
                        "Image Tag Mutability": repo.get("imageTagMutability", "N/A"),
                        "Encryption": repo.get("encryptionConfiguration", {}).get("encryptionType", "N/A"),
                        "KMS Key": repo.get("encryptionConfiguration", {}).get("kmsKey", "N/A"),
                        "Created At": created,
                        "Region": region,
                        "Account ID": acct_id,
                        "Account Name": acct_name,
                        "Environment": acct_env,
                        "Tags": str(tags)
                    })

        except ClientError:
            continue

    # Cache results
    ecr_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results
    }

    return results

# ----------------------------------------------------------------------
# S3 Functions (Storage, Object Count, Encryption, Public Access)
# ----------------------------------------------------------------------

def find_s3_for_account(account, master_session, s3_cache):
    """
    Scan S3 buckets in the account and return metadata including:
    - Region, CreateDate, Encryption, PublicAccessBlock
    - Object Count, Total Size GB, Storage Class
    - Cost Estimate (very rough: $0.023/GB for standard)
    """

    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    if is_cache_valid(acct_id, s3_cache):
        return s3_cache[acct_id]["data"]

    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    s3 = session.client("s3")
    results = []

    try:
        buckets = s3.list_buckets().get("Buckets", [])
    except ClientError:
        return []

    for bucket in buckets:
        bucket_name = bucket["Name"]
        created = bucket.get("CreationDate")

        # Defaults before lookup
        region = "N/A"
        encryption = "None"
        kms_key = "N/A"
        public_access = "Unknown"
        tags = {}
        object_count = None
        total_bytes = None
        storage_class = "Standard"

        # Bucket region
        try:
            loc = s3.get_bucket_location(Bucket=bucket_name)
            raw_region = loc.get("LocationConstraint")
            if raw_region in (None, "", "EU"):
                # None => us-east-1, "EU" => eu-west-1 legacy quirk
                region = "us-east-1" if raw_region is None else "eu-west-1"
            else:
                region = raw_region
        except ClientError:
            region = "us-east-1"

        # Always ensure region is valid
        if region == "N/A" or not isinstance(region, str):
            region = "us-east-1"

        # Create region-specific CloudWatch client
        cw = session.client("cloudwatch", region_name=region)

        # Encryption
        try:
            enc = s3.get_bucket_encryption(Bucket=bucket_name)
            rule = enc["ServerSideEncryptionConfiguration"]["Rules"][0]["ApplyServerSideEncryptionByDefault"]
            encryption = rule.get("SSEAlgorithm")
            kms_key = rule.get("KMSMasterKeyID", "N/A")
        except ClientError:
            pass

        # Public Access Block
        try:
            pab = s3.get_public_access_block(Bucket=bucket_name)
            cfg = pab["PublicAccessBlockConfiguration"]
            public_access = "Blocked" if all(cfg.values()) else "Partially Allowed"
        except ClientError:
            public_access = "Unknown"

        # Tags
        try:
            tag_resp = s3.get_bucket_tagging(Bucket=bucket_name)
            tags = {t["Key"]: t["Value"] for t in tag_resp.get("TagSet", [])}
        except ClientError:
            pass

        # ----- CloudWatch Metrics (Size/ObjectCount/StorageClass) -----
        try:
            metrics = cw.get_metric_data(
                MetricDataQueries=[
                    {
                        "Id": "size",
                        "MetricStat": {
                            "Metric": {
                                "Namespace": "AWS/S3",
                                "MetricName": "BucketSizeBytes",
                                "Dimensions": [
                                    {"Name": "BucketName", "Value": bucket_name},
                                    {"Name": "StorageType", "Value": "StandardStorage"}
                                ]
                            },
                            "Period": 86400,
                            "Stat": "Average"
                        }
                    },
                    {
                        "Id": "object_count",
                        "MetricStat": {
                            "Metric": {
                                "Namespace": "AWS/S3",
                                "MetricName": "NumberOfObjects",
                                "Dimensions": [
                                    {"Name": "BucketName", "Value": bucket_name},
                                    {"Name": "StorageType", "Value": "AllStorageTypes"}
                                ]
                            },
                            "Period": 86400,
                            "Stat": "Average"
                        }
                    }
                ],
                StartTime=datetime.now(UTC)- timedelta(days=3),
                EndTime=datetime.now(UTC)
            )

            size_vals = metrics["MetricDataResults"][0].get("Values", [])
            count_vals = metrics["MetricDataResults"][1].get("Values", [])

            total_bytes = max(size_vals) if size_vals else 0
            object_count = max(count_vals) if count_vals else 0

        except ClientError:
            total_bytes = None
            object_count = None

        # Convert size to GB
        total_gb = round(total_bytes / (1024**3), 2) if total_bytes else 0

        # Cost estimate (very rough, standard tier only)
        cost_usd = round(total_gb * 0.023, 2)

        results.append({
            "BucketName": bucket_name,
            "Region": region,
            "CreateDate": created,
            "StorageClass": storage_class,
            "ObjectCount": object_count,
            "TotalSizeGB": total_gb,
            "Encryption": encryption,
            "PublicAccessBlock": public_access,
            "Tags": str(tags),
            "CostEstimateUSD": cost_usd,
            "AccountID": acct_id,
            "AccountName": acct_name,
            "Environment": acct_env,
        })

    # Store in cache
    s3_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results
    }

    return results

# ----------------------------------------------------------------------
# CloudWatch Functions
# ----------------------------------------------------------------------

def find_cloudwatch_for_account(account, master_session, regions, cw_cache):
    """
    Inventory CloudWatch across an account:
    - Count custom metric namespaces
    - Count metrics
    - Count alarms
    - Log Groups & retention
    - Estimated log storage cost
    """

    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    if is_cache_valid(acct_id, cw_cache):
        return cw_cache[acct_id]["data"]

    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []

    for region in regions:
        try:
            cw = session.client("cloudwatch", region_name=region)
            logs = session.client("logs", region_name=region)

            # ---------------- Metrics / Namespaces ----------------
            metric_count = 0
            namespaces = set()

            paginator = cw.get_paginator("list_metrics")
            for page in paginator.paginate():
                for m in page.get("Metrics", []):
                    namespaces.add(m.get("Namespace"))
                    metric_count += 1

            # ---------------- Alarms ----------------
            alarm_count = 0
            alarm_paginator = cw.get_paginator("describe_alarms")
            for page in alarm_paginator.paginate():
                alarm_count += len(page.get("MetricAlarms", [])) + len(page.get("CompositeAlarms", []))

            # ---------------- Logs Groups ----------------
            logs_groups = []
            total_log_bytes = 0

            log_paginator = logs.get_paginator("describe_log_groups")
            for page in log_paginator.paginate():
                for lg in page.get("logGroups", []):
                    name = lg.get("logGroupName")
                    ret = lg.get("retentionInDays", "Never")
                    stored_bytes = lg.get("storedBytes", 0)

                    total_log_bytes += stored_bytes

                    logs_groups.append({
                        "LogGroup": name,
                        "RetentionDays": ret,
                        "StoredBytes": stored_bytes
                    })

            # Convert logs size to GB
            total_gb = round(total_log_bytes / (1024 ** 3), 3) if total_log_bytes else 0

            # Logging cost: $0.03 per GB-month (standard ingest pricing)
            cost_estimate = round(total_gb * 0.03, 2)

            results.append({
                "MetricNamespaceCount": len(namespaces),
                "MetricCount": metric_count,
                "AlarmsCount": alarm_count,
                "LogsGroups": len(logs_groups),
                "RetentionDays": ", ".join(
                    sorted({str(g["RetentionDays"]) for g in logs_groups})
                ),
                "CostEstimateUSD": cost_estimate,
                "Region": region,
                "AccountID": acct_id,
                "AccountName": acct_name,
                "Environment": acct_env,
                "LogGroupsDetail": str(logs_groups),
            })

        except ClientError:
            continue

    cw_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results
    }

    return results

# ----------------------------------------------------------------------
# VPC Functions
# ----------------------------------------------------------------------

def find_vpc_for_account(account, master_session, regions, vpc_cache):
    """
    Inventory VPCs for a single AWS account.
    Returns: VPC metadata including:
    - CIDR, Default, Subnet Count, RouteTables, IGW, NAT count, Flow Logs, Tags, Cost
    """

    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    if is_cache_valid(acct_id, vpc_cache):
        return vpc_cache[acct_id]["data"]

    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []

    for region in regions:
        try:
            ec2 = session.resource("ec2", region_name=region)
            logs = session.client("logs", region_name=region)

            for vpc in ec2.vpcs.all():

                # ---------------- Subnets ----------------
                subnets = list(vpc.subnets.all())
                subnet_count = len(subnets)

                # ---------------- Route Tables ----------------
                route_tables = list(vpc.route_tables.all())
                route_table_count = len(route_tables)

                # ---------------- Internet Gateway ----------------
                igw_id = "N/A"
                try:
                    for igw in ec2.internet_gateways.filter(
                        Filters=[{"Name": "attachment.vpc-id", "Values": [vpc.id]}]
                    ):
                        igw_id = igw.id
                        break
                except ClientError:
                    pass

                # ---------------- NAT Gateways ----------------
                nat_count = 0
                try:
                    nat_client = session.client("ec2", region_name=region)
                    nat_resp = nat_client.describe_nat_gateways(
                        Filter=[{"Name": "vpc-id", "Values": [vpc.id]}]
                    )
                    nat_count = len(nat_resp.get("NatGateways", []))
                except ClientError:
                    pass

                # ---------------- Flow Logs ----------------
                flow_logs_enabled = "No"
                try:
                    fl_client = session.client("ec2", region_name=region)
                    fl_resp = fl_client.describe_flow_logs(
                        Filter=[{"Name": "resource-id", "Values": [vpc.id]}]
                    )
                    if fl_resp.get("FlowLogs"):
                        flow_logs_enabled = "Yes"
                except ClientError:
                    pass

                # ---------------- Tags ----------------
                tags = {t["Key"]: t.get("Value", "") for t in (vpc.tags or [])}

                # ---------------- Cost Estimate ----------------
                # NAT Gateway cost (~$32/mo each) simplified estimate
                cost_usd = round(nat_count * 32.00, 2)

                results.append({
                    "VpcId": vpc.id,
                    "CidrBlock": vpc.cidr_block,
                    "State": vpc.state,
                    "Default": vpc.is_default,
                    "Subnets": subnet_count,
                    "RouteTables": route_table_count,
                    "InternetGatewayId": igw_id,
                    "NatGatewayCount": nat_count,
                    "FlowLogsEnabled": flow_logs_enabled,
                    "Tags": str(tags),
                    "CostEstimateUSD": cost_usd,
                    "Region": region,
                    "AccountID": acct_id,
                    "AccountName": acct_name,
                    "Environment": acct_env,
                })

        except ClientError:
            continue

    vpc_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results
    }

    return results

# ----------------------------------------------------------------------
# SecurityHub Functions
# ----------------------------------------------------------------------

def find_securityhub_for_account(account, master_session, regions, sh_cache):
    """
    Scan SecurityHub for a single AWS account.
    Returns:
        - Standards enabled
        - Total findings
        - CostEstimateUSD (very rough)
    """

    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    # Use cache if still valid
    if is_cache_valid(acct_id, sh_cache):
        return sh_cache[acct_id]["data"]

    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []

    for region in regions:
        try:
            sh = session.client("securityhub", region_name=region)

            # ---------------- Standards Enabled ----------------
            standards_cnt = 0
            try:
                paginator = sh.get_paginator("get_enabled_standards")
                for page in paginator.paginate():
                    standards_cnt += len(page.get("StandardsSubscriptions", []))
            except ClientError:
                standards_cnt = "N/A"

            # ---------------- Findings Count ----------------
            findings_cnt = 0
            try:
                paginator = sh.get_paginator("get_findings")
                for page in paginator.paginate():
                    findings_cnt += len(page.get("Findings", []))
            except ClientError:
                findings_cnt = "N/A"

            # ---------------- Cost Estimate ----------------
            # VERY rough placeholder: $0.001 per finding per month
            if isinstance(findings_cnt, int):
                cost_est = round(findings_cnt * 0.001, 4)
            else:
                cost_est = "N/A"

            results.append({
                "StandardsEnabled": standards_cnt,
                "FindingsCount": findings_cnt,
                "CostEstimateUSD": cost_est,
                "Region": region,
                "AccountID": acct_id,
                "AccountName": acct_name,
                "Environment": acct_env,
            })

        except ClientError:
            continue

    # Cache results
    sh_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results
    }

    return results

    # ----------------------------------------------------------------------
# GuardDuty Functions
# ----------------------------------------------------------------------

def find_guardduty_for_account(account, master_session, regions, gd_cache):
    """
    Inventory GuardDuty for a single AWS account:
    - Detector ID
    - Status (ENABLED / DISABLED)
    - FindingsCount
    - Cost Estimate (very rough: $0.0004 per finding per month)
    """

    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    # Use cache if still valid
    if is_cache_valid(acct_id, gd_cache):
        return gd_cache[acct_id]["data"]

    # Assume role if not master
    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []

    for region in regions:
        try:
            gd = session.client("guardduty", region_name=region)

            # ---------------- Get Detectors ----------------
            try:
                resp = gd.list_detectors()
                detectors = resp.get("DetectorIds", [])
            except ClientError:
                detectors = []

            if not detectors:
                # No detectors in this region
                results.append({
                    "DetectorId": "None",
                    "Status": "DISABLED",
                    "FindingsCount": 0,
                    "CostEstimateUSD": 0,
                    "Region": region,
                    "AccountID": acct_id,
                    "AccountName": acct_name,
                    "Environment": acct_env,
                })
                continue

            detector_id = detectors[0]

            # ---------------- Detector Status ----------------
            try:
                det = gd.get_detector(DetectorId=detector_id)
                status = det.get("Status", "Unknown")
            except ClientError:
                status = "Unknown"

            # ---------------- Findings Count ----------------
            findings_count = 0
            try:
                paginator = gd.get_paginator("list_findings")
                for page in paginator.paginate(DetectorId=detector_id):
                    findings_count += len(page.get("FindingIds", []))
            except ClientError:
                findings_count = "N/A"

            # ---------------- Cost Estimate ----------------
            # GuardDuty pricing: ~$0.0004 per finding analyzed
            if isinstance(findings_count, int):
                cost_est = round(findings_count * 0.0004, 4)
            else:
                cost_est = "N/A"

            results.append({
                "DetectorId": detector_id,
                "Status": status,
                "FindingsCount": findings_count,
                "CostEstimateUSD": cost_est,
                "Region": region,
                "AccountID": acct_id,
                "AccountName": acct_name,
                "Environment": acct_env,
            })

        except ClientError:
            continue

    # Cache results
    gd_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results
    }

    return results

# ----------------------------------------------------------------------
# Inspector Functions (Inspector2)
# ----------------------------------------------------------------------



def find_inspector_for_account(account, master_session, regions, inspector_cache):
    """
    Inventory AWS Inspector2 for a single AWS account:
    - Enabled Resource Types
    - Findings Count (with severity breakdown)
    - Cost Estimate (very rough: ~$0.02 per finding)
    """

    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    # Use cache if valid
    if is_cache_valid(acct_id, inspector_cache):
        return inspector_cache[acct_id]["data"]

    # Assume role if not master
    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []

    for region in regions:
        try:
            insp = session.client("inspector2", region_name=region)

            # ---------------- Enabled Resource Types ----------------
            enabled_types = []
            try:
                status_resp = insp.batch_get_account_status(accountIds=[acct_id])
                accounts_data = status_resp.get("accounts", [])
                if accounts_data:
                    enabled_types = [
                        k for k, v in accounts_data[0].get("resourceState", {}).items()
                        if v.get("status") == "ENABLED"
                    ]
            except ClientError:
                pass

            # ---------------- Findings and Severity Breakdown ----------------
            findings_count = 0
            severity_count = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFORMATIONAL": 0, "UNTRIAGED": 0}

            try:
                paginator = insp.get_paginator("list_findings")
                for page in paginator.paginate():
                    findings = page.get("findings", [])
                    findings_count += len(findings)
                    for f in findings:
                        sev = f.get("severity", "UNTRIAGED").upper()
                        if sev in severity_count:
                            severity_count[sev] += 1
                        else:
                            severity_count["UNTRIAGED"] += 1
            except ClientError:
                pass

            # ---------------- Cost Estimate ----------------
            cost_est = round(findings_count * 0.02, 2)

            results.append({
                "Region": region,
                "EnabledResourceTypes": ", ".join(enabled_types) or "None",
                "FindingsCount": findings_count,
                "CriticalFindings": severity_count["CRITICAL"],
                "HighFindings": severity_count["HIGH"],
                "MediumFindings": severity_count["MEDIUM"],
                "LowFindings": severity_count["LOW"],
                "InformationalFindings": severity_count["INFORMATIONAL"],
                "UntriagedFindings": severity_count["UNTRIAGED"],
                "CostEstimateUSD": cost_est,
                "AccountID": acct_id,
                "AccountName": acct_name,
                "Environment": acct_env,
            })

        except EndpointConnectionError:
            # Region doesn’t support Inspector2
            continue
        except ClientError:
            continue

    # Cache results
    inspector_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results
    }

    return results


# ----------------------------------------------------------------------
# Macie Functions (Macie2)
# ----------------------------------------------------------------------


def find_macie_for_account(account, master_session, regions, macie_cache):
    """
    Inventory AWS Macie2 for a single AWS account:
    - S3BucketCount (from job targets)
    - FindingsCount
    - CostEstimateUSD (rough estimate: ~$1 per 1k findings)
    """

    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    if is_cache_valid(acct_id, macie_cache):
        return macie_cache[acct_id]["data"]

    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []

    for region in regions:
        try:
            macie = session.client("macie2", region_name=region)

            # --- Check if Macie is enabled ---
            try:
                session_status = macie.get_macie_session()
                status = session_status.get("status", "DISABLED")
                if status != "ENABLED":
                    continue  # Skip disabled accounts
            except ClientError:
                continue

            # --- Findings Count ---
            findings_count = 0
            try:
                paginator = macie.get_paginator("list_findings")
                for page in paginator.paginate():
                    findings_count += len(page.get("findingIds", []))
            except ClientError:
                pass

            # --- Approximate S3 Buckets Scanned ---
            s3_bucket_count = 0
            try:
                paginator = macie.get_paginator("list_classification_jobs")
                for page in paginator.paginate():
                    for job in page.get("items", []):
                        if "s3JobDefinition" in job:
                            targets = job["s3JobDefinition"].get("bucketDefinitions", [])
                            s3_bucket_count += len(targets)
            except ClientError:
                pass

            # --- Cost Estimate ---
            cost_est = round(findings_count * 0.001, 2)

            results.append({
                "Region": region,
                "S3BucketCount": s3_bucket_count,
                "FindingsCount": findings_count,
                "CostEstimateUSD": cost_est,
                "AccountID": acct_id,
                "AccountName": acct_name,
                "Environment": acct_env,
            })

        except EndpointConnectionError:
            continue
        except ClientError:
            continue

    macie_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results
    }

    return results

# ----------------------------------------------------------------------
# AWS Config Functions
# ----------------------------------------------------------------------

def find_config_for_account(account, master_session, regions, config_cache):
    """
    Inventory AWS Config across an account:
    - Recorders: Count of configuration recorders
    - Rules: Count of Config rules
    - NonCompliantResources: Count of non-compliant rule evaluations
    - CostEstimateUSD: Rough ~$0.001 per non-compliant resource per month
    """

    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    if is_cache_valid(acct_id, config_cache):
        return config_cache[acct_id]["data"]

    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []

    for region in regions:
        try:
            cfg = session.client("config", region_name=region)

            # --- Recorders ---
            try:
                rec = cfg.describe_configuration_recorders()
                recorder_count = len(rec.get("ConfigurationRecorders", []))
            except ClientError:
                recorder_count = 0

            # --- Rules & Compliance ---
            rule_count = 0
            non_compliant_count = 0

            try:
                rule_paginator = cfg.get_paginator("describe_config_rules")
                for page in rule_paginator.paginate():
                    rules = page.get("ConfigRules", [])
                    rule_count += len(rules)

                    # Get compliance for each rule
                    for rule in rules:
                        rule_name = rule.get("ConfigRuleName")
                        try:
                            comp = cfg.get_compliance_details_by_config_rule(
                                ConfigRuleName=rule_name,
                                ComplianceTypes=["NON_COMPLIANT"]
                            )
                            non_compliant_count += len(comp.get("EvaluationResults", []))
                        except ClientError:
                            pass

            except ClientError:
                rule_count = 0
                non_compliant_count = 0

            # --- Cost Estimate ---
            # Rough estimate: ~$0.001 per non-compliant resource
            cost_est = round(non_compliant_count * 0.001, 4)

            results.append({
                "Recorders": recorder_count,
                "Rules": rule_count,
                "NonCompliantResources": non_compliant_count,
                "CostEstimateUSD": cost_est,
                "Region": region,
                "AccountID": acct_id,
                "AccountName": acct_name,
                "Environment": acct_env
            })

        except ClientError:
            continue

    config_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results
    }
    return results

# ----------------------------------------------------------------------
# IAM Functions
# ----------------------------------------------------------------------

def find_iam_for_account(account, master_session, iam_cache):
    """
    Inventory IAM for a single AWS account.
    Returns:
    - IAMUsers: count
    - IAMRoles: count
    - MFAEnabled: count of users with MFA devices
    - Tags: user/role tag map (flattened)
    """

    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    # IAM is global — no regional loop required
    if is_cache_valid(acct_id, iam_cache):
        return iam_cache[acct_id]["data"]

    # Assume role if not master account
    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    iam = session.client("iam")

    user_count = 0
    role_count = 0
    mfa_enabled_count = 0
    tags_summary = []

    try:
        # ---- Users ----
        paginator = iam.get_paginator("list_users")
        for page in paginator.paginate():
            for user in page.get("Users", []):
                user_count += 1

                # MFA check
                try:
                    mfa_resp = iam.list_mfa_devices(UserName=user["UserName"])
                    if mfa_resp.get("MFADevices"):
                        mfa_enabled_count += 1
                except ClientError:
                    pass

                # Tags
                try:
                    tag_resp = iam.list_user_tags(UserName=user["UserName"])
                    if tag_resp.get("Tags"):
                        tags_summary.append({
                            "Type": "User",
                            "Name": user["UserName"],
                            "Tags": tag_resp.get("Tags")
                        })
                except ClientError:
                    pass

        # ---- Roles ----
        paginator = iam.get_paginator("list_roles")
        for page in paginator.paginate():
            for role in page.get("Roles", []):
                role_count += 1

                try:
                    tag_resp = iam.list_role_tags(RoleName=role["RoleName"])
                    if tag_resp.get("Tags"):
                        tags_summary.append({
                            "Type": "Role",
                            "Name": role["RoleName"],
                            "Tags": tag_resp.get("Tags")
                        })
                except ClientError:
                    pass

    except ClientError:
        pass

    results = [{
        "IAMUsers": user_count,
        "IAMRoles": role_count,
        "MFAEnabled": mfa_enabled_count,
        "Tags": str(tags_summary),
        "AccountID": acct_id,
        "AccountName": acct_name,
        "Environment": acct_env,
        "Region": "global"
    }]

    # Cache
    iam_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results
    }

    return results

# ----------------------------------------------------------------------
# DynamoDB Functions
# ----------------------------------------------------------------------

def find_dynamodb_for_account(account, master_session, regions, dynamodb_cache):
    """
    Inventory DynamoDB tables:
    - TableName
    - ItemCount
    - TableSizeBytes
    - ReadCapacity
    - WriteCapacity
    - Tags
    - CostEstimateUSD (approx: $0.25/GB storage)
    """

    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    if is_cache_valid(acct_id, dynamodb_cache):
        return dynamodb_cache[acct_id]["data"]

    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []

    for region in regions:
        try:
            dynamo = session.client("dynamodb", region_name=region)

            paginator = dynamo.get_paginator("list_tables")
            table_names = []

            for page in paginator.paginate():
                table_names.extend(page.get("TableNames", []))

            for name in table_names:
                try:
                    desc = dynamo.describe_table(TableName=name)
                    tbl = desc.get("Table", {})

                    # Read/Write capacity (works for provisioned & on-demand)
                    if "ProvisionedThroughput" in tbl:
                        rc = tbl["ProvisionedThroughput"].get("ReadCapacityUnits", "On-Demand")
                        wc = tbl["ProvisionedThroughput"].get("WriteCapacityUnits", "On-Demand")
                    else:
                        rc, wc = "On-Demand", "On-Demand"

                    # Tags
                    try:
                        tag_resp = dynamo.list_tags_of_resource(
                            ResourceArn=tbl.get("TableArn")
                        )
                        tags = {t["Key"]: t.get("Value", "") for t in tag_resp.get("Tags", [])}
                    except ClientError:
                        tags = {}

                    # Cost: Approx $0.25/GB storage
                    size_gb = round(tbl.get("TableSizeBytes", 0) / (1024**3), 3)
                    cost = round(size_gb * 0.25, 2)

                    results.append({
                        "TableName": tbl.get("TableName"),
                        "ItemCount": tbl.get("ItemCount"),
                        "TableSizeBytes": tbl.get("TableSizeBytes"),
                        "ReadCapacity": rc,
                        "WriteCapacity": wc,
                        "Tags": str(tags),
                        "CostEstimateUSD": cost,
                        "Region": region,
                        "AccountID": acct_id,
                        "AccountName": acct_name,
                        "Environment": acct_env,
                    })

                except ClientError:
                    continue

        except ClientError:
            continue

    dynamodb_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results
    }

    return results

# ----------------------------------------------------------------------
# Glue Functions
# ----------------------------------------------------------------------

def find_glue_for_account(account, master_session, regions, glue_cache):
    """
    Inventory AWS Glue Jobs:
    - JobName
    - State (Enabled/Disabled)
    - LastRunTime
    - Tags
    - CostEstimateUSD (very rough: $0.44 per DPU-hour)
    """
    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    if is_cache_valid(acct_id, glue_cache):
        return glue_cache[acct_id]["data"]

    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []

    for region in regions:
        try:
            glue = session.client("glue", region_name=region)
            paginator = glue.get_paginator("get_jobs")

            for page in paginator.paginate():
                for job in page.get("Jobs", []):
                    job_name = job.get("Name")
                    job_tags = {}

                    # ---------- SAFE TAG HANDLING ----------
                    role_arn = job.get("RoleArn")

                    if role_arn:
                        try:
                            tag_resp = glue.get_tags(ResourceArn=role_arn)
                            job_tags = tag_resp.get("Tags", {})
                        except ClientError as e:
                            print(f"Warning: could not fetch tags for Glue job '{job_name}' role {role_arn}: {e}")
                    else:
                        print(f"Glue Job '{job_name}' has no RoleArn - skipping tag lookup")
                    # --------------------------------------

                    state = "Enabled"

                    # Last run time from job runs
                    last_run_time = "N/A"
                    try:
                        runs = glue.get_job_runs(JobName=job_name, MaxResults=1)
                        if runs.get("JobRuns"):
                            last_run_time = runs["JobRuns"][0].get("CompletedOn", "N/A")
                    except ClientError as e:
                        print(f"Failed retrieving job runs for {job_name}: {e}")

                    # Cost estimate baseline
                    cost_usd = 0.44

                    results.append({
                        "JobName": job_name,
                        "State": state,
                        "LastRunTime": last_run_time,
                        "Tags": str(job_tags),
                        "CostEstimateUSD": cost_usd,
                        "Region": region,
                        "AccountID": acct_id,
                        "AccountName": acct_name,
                        "Environment": acct_env,
                    })

        except ClientError as e:
            print(f"Glue scan failed in region {region} for account {acct_id}: {e}")
            continue

    glue_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results
    }

    return results

# ----------------------------------------------------------------------
# DataSync Functions
# ----------------------------------------------------------------------

def find_datasync_for_account(account, master_session, regions, datasync_cache):
    """
    Inventory AWS DataSync tasks.
    - TaskName
    - Source
    - Destination
    - BytesTransferred
    - CostEstimateUSD (~$0.0125 per GB)
    """
    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    # Use cache if still valid
    if is_cache_valid(acct_id, datasync_cache):
        return datasync_cache[acct_id]["data"]

    # Assume role if needed
    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []

    for region in regions:
        try:
            ds = session.client("datasync", region_name=region)
            paginator = ds.get_paginator("list_tasks")

            for page in paginator.paginate():
                for task in page.get("Tasks", []):
                    task_arn = task.get("TaskArn")
                    task_name = task.get("Name", "N/A")

                    try:
                        desc = ds.describe_task(TaskArn=task_arn)
                        src = desc.get("SourceLocationArn", "N/A")
                        dst = desc.get("DestinationLocationArn", "N/A")

                        # Get recent execution metrics (latest TaskExecution)
                        bytes_transferred = 0
                        exec_paginator = ds.get_paginator("list_task_executions")
                        for exec_page in exec_paginator.paginate(TaskArn=task_arn):
                            for ex in exec_page.get("TaskExecutions", []):
                                exec_arn = ex.get("TaskExecutionArn")
                                try:
                                    exec_desc = ds.describe_task_execution(TaskExecutionArn=exec_arn)
                                    bytes_transferred = max(
                                        bytes_transferred,
                                        exec_desc.get("BytesTransferred", 0)
                                    )
                                except ClientError:
                                    continue

                        # Convert to GB and estimate cost
                        gb = round(bytes_transferred / (1024**3), 3)
                        cost = round(gb * 0.0125, 3)

                        results.append({
                            "TaskName": task_name,
                            "Source": src,
                            "Destination": dst,
                            "BytesTransferred": bytes_transferred,
                            "CostEstimateUSD": cost,
                            "Region": region,
                            "AccountID": acct_id,
                            "AccountName": acct_name,
                            "Environment": acct_env,
                        })

                    except ClientError:
                        continue

        except ClientError:
            continue

    # Cache results
    datasync_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results,
    }

    return results

# ----------------------------------------------------------------------
# Kinesis Functions
# ----------------------------------------------------------------------

def find_kinesis_for_account(account, master_session, regions, kinesis_cache):
    """
    Inventory AWS Kinesis Data Streams.
    - StreamName
    - ShardCount
    - RetentionHours
    - Status
    - CostEstimateUSD (~$0.015 per shard-hour)
    """

    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    # Use cache if valid
    if is_cache_valid(acct_id, kinesis_cache):
        return kinesis_cache[acct_id]["data"]

    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []

    for region in regions:
        try:
            kin = session.client("kinesis", region_name=region)
            paginator = kin.get_paginator("list_streams")

            for page in paginator.paginate():
                for stream_name in page.get("StreamNames", []):
                    try:
                        desc = kin.describe_stream_summary(StreamName=stream_name)
                        stream = desc.get("StreamDescriptionSummary", {})

                        shard_count = stream.get("OpenShardCount", 0)
                        retention_hours = stream.get("RetentionPeriodHours", 24)
                        status = stream.get("StreamStatus", "Unknown")

                        # Cost estimate (~$0.015/shard-hour × 720h per month)
                        cost_usd = round(shard_count * 720 * 0.015, 2)

                        results.append({
                            "StreamName": stream_name,
                            "ShardCount": shard_count,
                            "RetentionHours": retention_hours,
                            "Status": status,
                            "CostEstimateUSD": cost_usd,
                            "Region": region,
                            "AccountID": acct_id,
                            "AccountName": acct_name,
                            "Environment": acct_env,
                        })

                    except ClientError:
                        continue

        except ClientError:
            continue

    # Cache results
    kinesis_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results
    }

    return results

# ----------------------------------------------------------------------
# KMS Functions
# ----------------------------------------------------------------------

def find_kms_for_account(account, master_session, regions, kms_cache):
    """
    Inventory KMS keys for a single account across all regions.
    - KeyId
    - KeyState
    - RotationEnabled
    - KeyManager (CUSTOMER / AWS)
    - Tags
    - CostEstimateUSD (~$1/mo per CMK)
    """

    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    if is_cache_valid(acct_id, kms_cache):
        return kms_cache[acct_id]["data"]

    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []

    for region in regions:
        try:
            kms = session.client("kms", region_name=region)

            # list keys in region
            paginator = kms.get_paginator("list_keys")
            for page in paginator.paginate():
                for key in page.get("Keys", []):
                    key_id = key.get("KeyId")
                    try:
                        # Describe key
                        meta = kms.describe_key(KeyId=key_id)
                        key_meta = meta.get("KeyMetadata", {})

                        key_state = key_meta.get("KeyState", "Unknown")
                        key_manager = key_meta.get("KeyManager", "Unknown")

                        # Rotation
                        try:
                            rot = kms.get_key_rotation_status(KeyId=key_id)
                            rotation_enabled = rot.get("KeyRotationEnabled", False)
                        except ClientError:
                            rotation_enabled = False

                        # Tags
                        try:
                            tag_resp = kms.list_resource_tags(KeyId=key_id)
                            tags = {t["TagKey"]: t.get("TagValue", "") for t in tag_resp.get("Tags", [])}
                        except ClientError:
                            tags = {}

                        # Cost: customer-managed CMK ~ $1/month
                        cost = 1.00 if key_manager == "CUSTOMER" else 0.00

                        results.append({
                            "KeyId": key_id,
                            "KeyState": key_state,
                            "RotationEnabled": rotation_enabled,
                            "KeyManager": key_manager,
                            "Tags": str(tags),
                            "CostEstimateUSD": cost,
                            "Region": region,
                            "AccountID": acct_id,
                            "AccountName": acct_name,
                            "Environment": acct_env,
                        })

                    except ClientError:
                        continue

        except ClientError:
            continue

    kms_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results
    }

    return results

# ----------------------------------------------------------------------
# Elastic Load Balancing (ELB/ALB/NLB) Functions
# ----------------------------------------------------------------------

def find_elb_for_account(account, master_session, regions, elb_cache):
    """
    Inventory Elastic Load Balancers (Classic, ALB, NLB, GWLB)
    - LoadBalancerName
    - DNSName
    - Type
    - Scheme
    - TargetGroups
    - Tags
    - CostEstimateUSD (~$0.025 per hour baseline)
    """
    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    # Use cache if valid
    if is_cache_valid(acct_id, elb_cache):
        return elb_cache[acct_id]["data"]

    # Assume role
    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []

    for region in regions:
        try:
            elbv2 = session.client("elbv2", region_name=region)
            elb = session.client("elb", region_name=region)

            # --- Application, Network, Gateway Load Balancers (ELBv2) ---
            paginator = elbv2.get_paginator("describe_load_balancers")
            for page in paginator.paginate():
                for lb in page.get("LoadBalancers", []):
                    lb_arn = lb.get("LoadBalancerArn")
                    lb_name = lb.get("LoadBalancerName")
                    lb_dns = lb.get("DNSName")
                    lb_type = lb.get("Type", "unknown")
                    lb_scheme = lb.get("Scheme", "unknown")

                    # Target Groups
                    target_groups = []
                    try:
                        tg_page = elbv2.describe_target_groups(LoadBalancerArn=lb_arn)
                        for tg in tg_page.get("TargetGroups", []):
                            target_groups.append(tg.get("TargetGroupName"))
                    except ClientError:
                        pass

                    # Tags
                    tags = {}
                    try:
                        tag_resp = elbv2.describe_tags(ResourceArns=[lb_arn])
                        for tag_desc in tag_resp.get("TagDescriptions", []):
                            for t in tag_desc.get("Tags", []):
                                tags[t["Key"]] = t.get("Value", "")
                    except ClientError:
                        pass

                    # Cost Estimate (baseline: ALB/NLB $0.025/hr + LCU usage $0.008/hr)
                    cost_usd = round(720 * (0.025 + 0.008), 2)  # monthly estimate per LB

                    results.append({
                        "LoadBalancerName": lb_name,
                        "DNSName": lb_dns,
                        "Type": lb_type,
                        "Scheme": lb_scheme,
                        "TargetGroups": ", ".join(target_groups),
                        "Tags": str(tags),
                        "CostEstimateUSD": cost_usd,
                        "Region": region,
                        "AccountID": acct_id,
                        "AccountName": acct_name,
                        "Environment": acct_env,
                    })

            # --- Classic Load Balancers (ELBv1) ---
            try:
                classic_page = elb.describe_load_balancers()
                for classic in classic_page.get("LoadBalancerDescriptions", []):
                    name = classic.get("LoadBalancerName")
                    dns = classic.get("DNSName")
                    scheme = "internet-facing" if classic.get("Scheme") == "internet-facing" else "internal"

                    # Classic ELBs don't have "Type" or Target Groups
                    tags = {}
                    try:
                        tag_resp = elb.describe_tags(LoadBalancerNames=[name])
                        for desc in tag_resp.get("TagDescriptions", []):
                            for t in desc.get("Tags", []):
                                tags[t["Key"]] = t.get("Value", "")
                    except ClientError:
                        pass

                    cost_usd = round(720 * 0.025, 2)

                    results.append({
                        "LoadBalancerName": name,
                        "DNSName": dns,
                        "Type": "classic",
                        "Scheme": scheme,
                        "TargetGroups": "N/A",
                        "Tags": str(tags),
                        "CostEstimateUSD": cost_usd,
                        "Region": region,
                        "AccountID": acct_id,
                        "AccountName": acct_name,
                        "Environment": acct_env,
                    })

            except ClientError:
                pass

        except ClientError:
            continue

    # Cache results
    elb_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results,
    }

    return results

# ----------------------------------------------------------------------
# Route 53 Functions
# ----------------------------------------------------------------------

def find_route53_for_account(account, master_session, route53_cache):
    """
    Inventory Route 53 hosted zones for a single AWS account.
    - HostedZoneId
    - RecordSetsCount
    - Tags
    - CostEstimateUSD (~$0.50 per hosted zone + $0.40 per million queries)
    """
    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    # Use cache if valid
    if is_cache_valid(acct_id, route53_cache):
        return route53_cache[acct_id]["data"]

    # Assume role unless master account
    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []
    try:
        r53 = session.client("route53")
        paginator = r53.get_paginator("list_hosted_zones")

        for page in paginator.paginate():
            for zone in page.get("HostedZones", []):
                zone_id = zone.get("Id", "").split("/")[-1]
                name = zone.get("Name", "").rstrip(".")
                private = zone.get("Config", {}).get("PrivateZone", False)

                # Count record sets
                try:
                    record_paginator = r53.get_paginator("list_resource_record_sets")
                    record_count = 0
                    for record_page in record_paginator.paginate(HostedZoneId=zone_id):
                        record_count += len(record_page.get("ResourceRecordSets", []))
                except ClientError:
                    record_count = "N/A"

                # Tags
                tags = {}
                try:
                    tag_resp = r53.list_tags_for_resource(
                        ResourceType="hostedzone", ResourceId=zone_id
                    )
                    for t in tag_resp.get("ResourceTagSet", {}).get("Tags", []):
                        tags[t["Key"]] = t.get("Value", "")
                except ClientError:
                    pass

                # Cost estimate: $0.50 per hosted zone/month (no query volume included)
                cost_usd = 0.50
                if private:
                    cost_usd += 0.10  # small premium for private zones

                results.append({
                    "HostedZoneId": zone_id,
                    "ZoneName": name,
                    "PrivateZone": private,
                    "RecordSetsCount": record_count,
                    "Tags": str(tags),
                    "CostEstimateUSD": cost_usd,
                    "AccountID": acct_id,
                    "AccountName": acct_name,
                    "Environment": acct_env,
                })

    except ClientError:
        pass

    route53_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results,
    }

    return results

# ----------------------------------------------------------------------
# WAF Functions (WAFv2)
# ----------------------------------------------------------------------

def find_waf_for_account(account, master_session, regions, waf_cache):
    """
    Inventory AWS WAFv2 for a single AWS account:
    - WebACLName, MetricName, RuleCount
    - CostEstimateUSD (rough: ~$1 per WebACL)
    """

    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    if is_cache_valid(acct_id, waf_cache):
        return waf_cache[acct_id]["data"]

    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []

    # WAFv2 supports both regional and global scopes
    scopes = ["REGIONAL", "CLOUDFRONT"]

    for region in regions:
        for scope in scopes:
            try:
                wafv2 = session.client("wafv2", region_name=region)

                # list_web_acls doesn't support pagination — handle manually
                resp = wafv2.list_web_acls(Scope=scope)
                web_acls = resp.get("WebACLs", [])

                while "NextMarker" in resp:
                    resp = wafv2.list_web_acls(Scope=scope, NextMarker=resp["NextMarker"])
                    web_acls.extend(resp.get("WebACLs", []))

                for acl in web_acls:
                    acl_name = acl.get("Name")
                    metric_name = acl.get("Id")

                    # Get full ACL details to count rules
                    rule_count = 0
                    try:
                        details = wafv2.get_web_acl(Name=acl_name, Scope=scope, Id=acl["Id"])
                        rule_count = len(details["WebACL"].get("Rules", []))
                    except ClientError:
                        pass

                    # Rough cost estimate ($1 per WebACL)
                    cost_est = 1.0

                    results.append({
                        "Region": region,
                        "Scope": scope,
                        "WebACLName": acl_name,
                        "MetricName": metric_name,
                        "RuleCount": rule_count,
                        "CostEstimateUSD": cost_est,
                        "AccountID": acct_id,
                        "AccountName": acct_name,
                        "Environment": acct_env,
                    })

            except EndpointConnectionError:
                continue
            except ClientError:
                continue

    waf_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results
    }

    return results

# ----------------------------------------------------------------------
# API Gateway (v1 and v2) Functions
# ----------------------------------------------------------------------

def find_apigateway_for_account(account, master_session, regions, apigw_cache):
    """
    Inventory AWS API Gateway (v1 and v2) APIs across regions.
    Collects:
    - ApiId
    - Name
    - ProtocolType
    - EndpointType
    - Tags
    - CostEstimateUSD (~$3.50 per million requests + small per-API baseline)
    """
    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    # Use cache if valid
    if is_cache_valid(acct_id, apigw_cache):
        return apigw_cache[acct_id]["data"]

    # Assume role
    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []

    for region in regions:
        # -------- API Gateway v2 (HTTP/WebSocket) --------
        try:
            apigw_v2 = session.client("apigatewayv2", region_name=region)
            paginator = apigw_v2.get_paginator("get_apis")
            for page in paginator.paginate():
                for api in page.get("Items", []):
                    api_id = api.get("ApiId")
                    name = api.get("Name", "N/A")
                    protocol = api.get("ProtocolType", "N/A")
                    endpoint = api.get("ApiEndpoint", "N/A")

                    # Tags
                    try:
                        tag_resp = apigw_v2.get_tags(ResourceArn=f"arn:aws:apigateway:{region}::/apis/{api_id}")
                        tags = tag_resp.get("Tags", {})
                    except ClientError:
                        tags = {}

                    # Cost estimate: baseline ~$1 per API/month
                    cost_usd = 1.00

                    results.append({
                        "ApiId": api_id,
                        "Name": name,
                        "ProtocolType": protocol,
                        "EndpointType": endpoint,
                        "Tags": str(tags),
                        "CostEstimateUSD": cost_usd,
                        "Version": "v2",
                        "Region": region,
                        "AccountID": acct_id,
                        "AccountName": acct_name,
                        "Environment": acct_env,
                    })
        except ClientError:
            pass

        # -------- API Gateway v1 (REST APIs) --------
        try:
            apigw_v1 = session.client("apigateway", region_name=region)
            paginator = apigw_v1.get_paginator("get_rest_apis")
            for page in paginator.paginate():
                for api in page.get("items", []):
                    api_id = api.get("id")
                    name = api.get("name", "N/A")

                    # Endpoint type
                    try:
                        stages = apigw_v1.get_stages(restApiId=api_id)
                        endpoint_type = "EDGE"
                        if stages.get("item"):
                            for stage in stages["item"]:
                                endpoint_type = stage.get("cacheClusterEnabled", False)
                        endpoint_type = "REGIONAL" if endpoint_type else "EDGE"
                    except ClientError:
                        endpoint_type = "Unknown"

                    # Tags
                    try:
                        tag_resp = apigw_v1.get_tags(resourceArn=f"arn:aws:apigateway:{region}::/restapis/{api_id}")
                        tags = tag_resp.get("tags", {})
                    except ClientError:
                        tags = {}

                    # Cost estimate
                    cost_usd = 1.00

                    results.append({
                        "ApiId": api_id,
                        "Name": name,
                        "ProtocolType": "REST",
                        "EndpointType": endpoint_type,
                        "Tags": str(tags),
                        "CostEstimateUSD": cost_usd,
                        "Version": "v1",
                        "Region": region,
                        "AccountID": acct_id,
                        "AccountName": acct_name,
                        "Environment": acct_env,
                    })
        except ClientError:
            continue

    apigw_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results,
    }

    return results

# ----------------------------------------------------------------------
# AppSync Functions
# ----------------------------------------------------------------------

def find_appsync_for_account(account, master_session, regions, appsync_cache):
    """
    Inventory AWS AppSync APIs across all regions.
    Collects:
    - ApiId
    - Name
    - AuthenticationType
    - Tags
    - CostEstimateUSD (~$4 per API/month + request-based cost)
    """
    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    # Use cache if valid
    if is_cache_valid(acct_id, appsync_cache):
        return appsync_cache[acct_id]["data"]

    # Assume role
    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []

    for region in regions:
        try:
            appsync = session.client("appsync", region_name=region)
            paginator = appsync.get_paginator("list_graphql_apis")

            for page in paginator.paginate():
                for api in page.get("graphqlApis", []):
                    api_id = api.get("apiId")
                    name = api.get("name", "N/A")
                    auth_type = api.get("authenticationType", "N/A")
                    arn = api.get("arn", "N/A")

                    # Get tags
                    try:
                        tag_resp = appsync.list_tags_for_resource(resourceArn=arn)
                        tags = tag_resp.get("tags", {})
                    except ClientError:
                        tags = {}

                    # Cost estimate: ~ $4 baseline per API per month
                    cost_usd = 4.00

                    results.append({
                        "ApiId": api_id,
                        "Name": name,
                        "AuthenticationType": auth_type,
                        "Tags": str(tags),
                        "CostEstimateUSD": cost_usd,
                        "Region": region,
                        "AccountID": acct_id,
                        "AccountName": acct_name,
                        "Environment": acct_env,
                    })

        except ClientError:
            continue

    appsync_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results,
    }

    return results

# ----------------------------------------------------------------------
# SageMaker Functions
# ----------------------------------------------------------------------

def find_sagemaker_for_account(account, master_session, regions, sagemaker_cache):
    """
    Inventory SageMaker notebook instances for a single AWS account.
    Collects:
    - NotebookName
    - InstanceType
    - Status
    - Tags
    - CostEstimateUSD (~$0.20/hr for ml.t3.medium -> ~$144/mo baseline)
    """
    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    # Use cache if valid
    if is_cache_valid(acct_id, sagemaker_cache):
        return sagemaker_cache[acct_id]["data"]

    # Assume role
    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []

    for region in regions:
        try:
            sm = session.client("sagemaker", region_name=region)
            paginator = sm.get_paginator("list_notebook_instances")

            for page in paginator.paginate():
                for nb in page.get("NotebookInstances", []):
                    nb_name = nb.get("NotebookInstanceName")
                    instance_type = nb.get("InstanceType", "N/A")
                    status = nb.get("NotebookInstanceStatus", "N/A")
                    arn = nb.get("NotebookInstanceArn")

                    # Get tags
                    try:
                        tag_resp = sm.list_tags(ResourceArn=arn)
                        tags = {t["Key"]: t.get("Value", "") for t in tag_resp.get("Tags", [])}
                    except ClientError:
                        tags = {}

                    # Cost estimate — baseline per notebook (varies by instance type)
                    hourly_rate = 0.20  # assume ml.t3.medium
                    monthly_estimate = round(hourly_rate * 24 * 30, 2)  # ~144 USD

                    results.append({
                        "NotebookName": nb_name,
                        "InstanceType": instance_type,
                        "Status": status,
                        "Tags": str(tags),
                        "CostEstimateUSD": monthly_estimate,
                        "Region": region,
                        "AccountID": acct_id,
                        "AccountName": acct_name,
                        "Environment": acct_env,
                    })

        except ClientError:
            continue

    sagemaker_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results,
    }

    return results

# ----------------------------------------------------------------------
# FSx Functions
# ----------------------------------------------------------------------

def find_fsx_for_account(account, master_session, regions, fsx_cache):
    """
    Inventory FSx file systems for a single AWS account.
    Collects:
    - FileSystemId
    - Type
    - SizeGiB
    - Status
    - Tags
    - CostEstimateUSD (~$0.13 per GB-month baseline)
    """
    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    # Use cache if valid
    if is_cache_valid(acct_id, fsx_cache):
        return fsx_cache[acct_id]["data"]

    # Assume role if needed
    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []

    for region in regions:
        try:
            fsx = session.client("fsx", region_name=region)
            paginator = fsx.get_paginator("describe_file_systems")

            for page in paginator.paginate():
                for fs in page.get("FileSystems", []):
                    fs_id = fs.get("FileSystemId")
                    fs_type = fs.get("FileSystemType", "N/A")
                    size_gib = fs.get("StorageCapacity", 0)
                    status = fs.get("Lifecycle", "N/A")
                    arn = fs.get("ResourceARN", f"arn:aws:fsx:{region}:{acct_id}:file-system/{fs_id}")

                    # Tags
                    try:
                        tag_resp = fsx.list_tags_for_resource(ResourceARN=arn)
                        tags = {t["Key"]: t.get("Value", "") for t in tag_resp.get("Tags", [])}
                    except ClientError:
                        tags = {}

                    # Estimate cost: $0.13 per GB-month (rough average across FSx types)
                    cost_usd = round(size_gib * 0.13, 2)

                    results.append({
                        "FileSystemId": fs_id,
                        "Type": fs_type,
                        "SizeGiB": size_gib,
                        "Status": status,
                        "Tags": str(tags),
                        "CostEstimateUSD": cost_usd,
                        "Region": region,
                        "AccountID": acct_id,
                        "AccountName": acct_name,
                        "Environment": acct_env,
                    })

        except ClientError:
            continue

    fsx_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results,
    }

    return results

# ----------------------------------------------------------------------
# WorkSpaces Functions
# ----------------------------------------------------------------------


def find_workspaces_for_account(account, master_session, regions, workspaces_cache):
    """
    Inventory Amazon WorkSpaces across a single AWS account.
    Collects:
    - WorkspaceId
    - BundleId
    - UserName
    - State
    - Tags
    - CostEstimateUSD (~$35–$75 per workspace/month typical)
    """

    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    # Use cache if valid
    if is_cache_valid(acct_id, workspaces_cache):
        return workspaces_cache[acct_id]["data"]

    # Assume role if not master
    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []

    for region in regions:
        try:
            ws = session.client("workspaces", region_name=region)

            # Some regions (like us-west-1) do not support WorkSpaces.
            # We’ll catch these errors and skip cleanly.
            try:
                paginator = ws.get_paginator("describe_workspaces")
            except Exception:
                continue

            for page in paginator.paginate():
                for w in page.get("Workspaces", []):
                    workspace_id = w.get("WorkspaceId")
                    bundle_id = w.get("BundleId", "N/A")
                    username = w.get("UserName", "N/A")
                    state = w.get("State", "N/A")

                    # Fetch tags safely
                    tags = {}
                    try:
                        tag_resp = ws.describe_tags(ResourceId=workspace_id)
                        tags = {t["Key"]: t.get("Value", "") for t in tag_resp.get("TagList", [])}
                    except ClientError:
                        pass

                    # Cost estimate — conservative $50 per workspace/month baseline
                    cost_usd = 50.00

                    results.append({
                        "WorkspaceId": workspace_id,
                        "BundleId": bundle_id,
                        "UserName": username,
                        "State": state,
                        "Tags": str(tags),
                        "CostEstimateUSD": cost_usd,
                        "Region": region,
                        "AccountID": acct_id,
                        "AccountName": acct_name,
                        "Environment": acct_env,
                    })

        except EndpointConnectionError:
            # Skip if the region has no endpoint for WorkSpaces
            continue
        except ClientError:
            continue
        except Exception:
            # Catch-all to prevent any single region from breaking the scan
            continue

    workspaces_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results
    }

    return results

# ----------------------------------------------------------------------
# Step Functions Functions
# ----------------------------------------------------------------------

def find_stepfunctions_for_account(account, master_session, regions, stepfunctions_cache):
    """
    Inventory AWS Step Functions across a single AWS account.
    Collects:
    - StateMachineName
    - Status
    - DefinitionSize (bytes)
    - Tags
    - CostEstimateUSD (~$0.025 per 1,000 state transitions)
    """
    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    # Use cache if valid
    if is_cache_valid(acct_id, stepfunctions_cache):
        return stepfunctions_cache[acct_id]["data"]

    # Assume role if not master
    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []

    for region in regions:
        try:
            sfn = session.client("stepfunctions", region_name=region)
            paginator = sfn.get_paginator("list_state_machines")

            for page in paginator.paginate():
                for sm in page.get("stateMachines", []):
                    sm_arn = sm.get("stateMachineArn")
                    sm_name = sm.get("name", "N/A")

                    # --- Status & Definition Size ---
                    try:
                        desc = sfn.describe_state_machine(stateMachineArn=sm_arn)
                        status = desc.get("status", "ACTIVE")
                        definition = desc.get("definition", "")
                        definition_size = len(definition.encode("utf-8"))
                    except ClientError:
                        status = "Unknown"
                        definition_size = 0

                    # --- Tags ---
                    try:
                        tag_resp = sfn.list_tags_for_resource(resourceArn=sm_arn)
                        tags = {t["key"]: t.get("value", "") for t in tag_resp.get("tags", [])}
                    except ClientError:
                        tags = {}

                    # --- Cost Estimate ---
                    # Step Functions cost ~$0.025 per 1,000 state transitions.
                    # Assume 10K monthly transitions per active machine = ~$0.25/month.
                    cost_usd = 0.25 if status == "ACTIVE" else 0.00

                    results.append({
                        "StateMachineName": sm_name,
                        "Status": status,
                        "DefinitionSize": definition_size,
                        "Tags": str(tags),
                        "CostEstimateUSD": cost_usd,
                        "Region": region,
                        "AccountID": acct_id,
                        "AccountName": acct_name,
                        "Environment": acct_env,
                    })

        except ClientError:
            continue

    stepfunctions_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results,
    }

    return results

# ----------------------------------------------------------------------
# AWS Backup Functions
# ----------------------------------------------------------------------

def find_backup_for_account(account, master_session, regions, backup_cache):
    """
    Inventory AWS Backup vaults across a single AWS account.
    Collects:
    - VaultName
    - RecoveryPoints
    - SizeBytes
    - CostEstimateUSD (~$0.05/GB-month for backup storage)
    """
    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    # Use cache if valid
    if is_cache_valid(acct_id, backup_cache):
        return backup_cache[acct_id]["data"]

    # Assume role if needed
    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []

    for region in regions:
        try:
            backup = session.client("backup", region_name=region)

            paginator = backup.get_paginator("list_backup_vaults")
            for page in paginator.paginate():
                for vault in page.get("BackupVaultList", []):
                    vault_name = vault.get("BackupVaultName", "N/A")
                    vault_arn = vault.get("BackupVaultArn")

                    # --- Count Recovery Points ---
                    try:
                        rp_paginator = backup.get_paginator("list_recovery_points_by_backup_vault")
                        recovery_points = 0
                        total_bytes = 0
                        for rp_page in rp_paginator.paginate(BackupVaultName=vault_name):
                            rps = rp_page.get("RecoveryPoints", [])
                            recovery_points += len(rps)
                            for rp in rps:
                                total_bytes += rp.get("BackupSizeInBytes", 0)
                    except ClientError:
                        recovery_points = 0
                        total_bytes = 0

                    # --- Tags ---
                    try:
                        tag_resp = backup.list_tags(ResourceArn=vault_arn)
                        tags = tag_resp.get("Tags", {})
                    except ClientError:
                        tags = {}

                    # --- Cost estimate ---
                    # AWS Backup storage ~ $0.05/GB-month for warm storage
                    size_gb = round(total_bytes / (1024 ** 3), 2)
                    cost_usd = round(size_gb * 0.05, 2)

                    results.append({
                        "VaultName": vault_name,
                        "RecoveryPoints": recovery_points,
                        "SizeBytes": total_bytes,
                        "CostEstimateUSD": cost_usd,
                        "Region": region,
                        "AccountID": acct_id,
                        "AccountName": acct_name,
                        "Environment": acct_env,
                        "Tags": str(tags),
                    })

        except ClientError:
            continue

    backup_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results,
    }

    return results

# ----------------------------------------------------------------------
# Direct Connect Functions
# ----------------------------------------------------------------------

def find_directconnect_for_account(account, master_session, regions, directconnect_cache):
    """
    Inventory AWS Direct Connect connections for a single account.
    Collects:
    - ConnectionId
    - Bandwidth
    - Location
    - State
    - CostEstimateUSD (~$0.25–$0.50/hr depending on port speed)
    """
    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    # Use cache if valid
    if is_cache_valid(acct_id, directconnect_cache):
        return directconnect_cache[acct_id]["data"]

    # Assume role if not master
    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []

    for region in regions:
        try:
            dc = session.client("directconnect", region_name=region)
            resp = dc.describe_connections()
            for conn in resp.get("connections", []):
                conn_id = conn.get("connectionId")
                bandwidth = conn.get("bandwidth", "N/A")
                location = conn.get("location", "N/A")
                state = conn.get("connectionState", "N/A")

                # Estimate monthly cost by bandwidth tier
                # Reference: typical DX pricing – approximate averages
                cost_map = {
                    "1Gbps": 360,      # ~$0.50/hr
                    "10Gbps": 2500,    # ~$3.40/hr
                    "100Gbps": 25000,  # newer 100 Gbps ports
                    "500Mbps": 180,
                    "200Mbps": 80,
                    "50Mbps": 25,
                }
                # fallback: parse number from bandwidth string
                key = bandwidth.replace(" ", "").replace("Port", "")
                cost_usd = cost_map.get(key, 360)  # default ~1 Gbps

                results.append({
                    "ConnectionId": conn_id,
                    "Bandwidth": bandwidth,
                    "Location": location,
                    "State": state,
                    "CostEstimateUSD": cost_usd,
                    "Region": region,
                    "AccountID": acct_id,
                    "AccountName": acct_name,
                    "Environment": acct_env,
                })

        except ClientError:
            continue

    directconnect_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results,
    }

    return results

# ----------------------------------------------------------------------
# Lightsail Functions
# ----------------------------------------------------------------------



def find_lightsail_for_account(account, master_session, regions, lightsail_cache):
    """
    Inventory AWS Lightsail instances for a single AWS account.
    Collects:
    - InstanceName, State, BlueprintId, BundleId, CreatedAt
    - CostEstimateUSD (rough: ~$5–$40 per instance/month)
    """

    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    # Use cache if valid
    if is_cache_valid(acct_id, lightsail_cache):
        return lightsail_cache[acct_id]["data"]

    # Assume role if not master
    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []

    # Only scan regions where Lightsail is actually available
    supported_regions = session.get_available_regions("lightsail")

    for region in regions:
        if region not in supported_regions:
            continue

        try:
            client = session.client("lightsail", region_name=region)

            # Lightsail supports pagination via NextPageToken, not paginator
            resp = client.get_instances()
            instances = resp.get("instances", [])

            while "nextPageToken" in resp:
                resp = client.get_instances(pageToken=resp["nextPageToken"])
                instances.extend(resp.get("instances", []))

            for inst in instances:
                name = inst.get("name")
                state = inst.get("state", {}).get("name", "Unknown")
                blueprint = inst.get("blueprintId", "N/A")
                bundle = inst.get("bundleId", "N/A")
                created = inst.get("createdAt", "N/A")

                # Rough cost estimate (~$10 per instance/month)
                cost_usd = 10.00

                results.append({
                    "InstanceName": name,
                    "State": state,
                    "BlueprintId": blueprint,
                    "BundleId": bundle,
                    "CreatedAt": str(created),
                    "CostEstimateUSD": cost_usd,
                    "Region": region,
                    "AccountID": acct_id,
                    "AccountName": acct_name,
                    "Environment": acct_env,
                })

        except EndpointConnectionError:
            # Region has no Lightsail endpoint
            continue
        except ClientError:
            continue
        except Exception:
            continue

    lightsail_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results
    }

    return results

# ----------------------------------------------------------------------
# CloudTrail Functions
# ----------------------------------------------------------------------

def find_cloudtrail_for_account(account, master_session, regions, cloudtrail_cache):
    """
    Inventory CloudTrail trails across all regions in an AWS account.
    Collects:
    - TrailName
    - IsMultiRegionTrail
    - LogFileValidationEnabled
    - S3BucketName
    - CostEstimateUSD (~$2 per 100,000 management events)
    """
    acct_id = account["Id"]
    acct_name = account["Name"]
    acct_env = account["Env"]

    # Use cache if valid
    if is_cache_valid(acct_id, cloudtrail_cache):
        return cloudtrail_cache[acct_id]["data"]

    # Assume role if not master
    session = master_session if acct_id == "123456789012" else assume_role(acct_id, master_session)
    if not session:
        return []

    results = []

    for region in regions:
        try:
            ct = session.client("cloudtrail", region_name=region)
            resp = ct.list_trails()

            for trail in resp.get("Trails", []):
                trail_name = trail.get("Name", "N/A")
                trail_arn = trail.get("TrailARN", "N/A")

                # Detailed description
                try:
                    desc = ct.describe_trails(trailNameList=[trail_name])
                    trail_info = desc.get("trailList", [])[0] if desc.get("trailList") else {}
                except ClientError:
                    trail_info = {}

                # Determine if validation & multi-region enabled
                multi_region = trail_info.get("IsMultiRegionTrail", False)
                log_validation = trail_info.get("LogFileValidationEnabled", False)
                s3_bucket = trail_info.get("S3BucketName", "N/A")

                # Approximate cost estimation
                # Assume 1 million events/month ≈ $20 baseline if enabled.
                cost_usd = 20.00 if trail_info else 0.00

                results.append({
                    "TrailName": trail_name,
                    "IsMultiRegionTrail": multi_region,
                    "LogFileValidationEnabled": log_validation,
                    "S3BucketName": s3_bucket,
                    "CostEstimateUSD": cost_usd,
                    "Region": region,
                    "AccountID": acct_id,
                    "AccountName": acct_name,
                    "Environment": acct_env,
                })

        except ClientError:
            continue

    cloudtrail_cache[acct_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results,
    }

    return results

# ----------------------------------------------------------------------
# Assume Role
# ----------------------------------------------------------------------

def assume_role(acct_id, master_session):
    """Assume OrganizationAccountAccessRole in a child account."""
    try:
        sts = master_session.client("sts")
        resp = sts.assume_role(
            RoleArn=f"arn:aws:iam::{acct_id}:role/OrganizationAccountAccessRole",
            RoleSessionName="MultiInventory"
        )

        return boto3.Session(
            aws_access_key_id=resp["Credentials"]["AccessKeyId"],
            aws_secret_access_key=resp["Credentials"]["SecretAccessKey"],
            aws_session_token=resp["Credentials"]["SessionToken"]
        )
    except ClientError:
        return None

# ----------------------------------------------------------------------
# Argument Parsing
# ----------------------------------------------------------------------

def parse_args():
    """Parse command-line args."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--profile_name",
        required=True,
        help="AWS CLI profile"
    )
    parser.add_argument(
        "-e", "--env",
        required=True,
        choices=["dev", "prod", "uat", "all"],
        help="Environment to scan"
    )

    return parser.parse_args()


def filter_accounts(env):
    """Return list of account IDs matching requested environment."""
    if env == "prod":
        return PROD_ACCOUNTS
    if env == "dev":
        return DEV_ACCOUNTS
    if env == "uat":
        return UAT_ACCOUNTS
    return PROD_ACCOUNTS + DEV_ACCOUNTS + UAT_ACCOUNTS

# ----------------------------------------------------------------------
# Main Execution
# ----------------------------------------------------------------------

def main():
    """Entry point."""
    args = parse_args()

    profile = args.profile_name
    env = args.env

    master_session = boto3.Session(profile_name=profile)
    org_client = master_session.client("organizations")

    ecs_cache = load_cache(ECS_CACHE_FILE)
    ec2_cache = load_cache(EC2_CACHE_FILE)
    ebs_cache = load_cache(EBS_CACHE_FILE)
    rds_cache = load_cache(RDS_CACHE_FILE)
    lambda_cache = load_cache(LAMBDA_CACHE_FILE)
    ecr_cache = load_cache(ECR_CACHE_FILE)
    s3_cache = load_cache(S3_CACHE_FILE)
    cw_cache = load_cache(CLOUDWATCH_CACHE_FILE)
    vpc_cache = load_cache(VPC_CACHE_FILE)
    sh_cache = load_cache(SECURITYHUB_CACHE_FILE)
    gd_cache = load_cache(GUARDDUTY_CACHE_FILE)
    inspector_cache = load_cache(INSPECTOR_CACHE_FILE)
    macie_cache = load_cache(MACIE_CACHE_FILE)
    config_cache = load_cache(CONFIG_CACHE_FILE)
    iam_cache = load_cache(IAM_CACHE_FILE)
    kms_cache = load_cache(KMS_CACHE_FILE)
    dynamodb_cache = load_cache(DYNAMODB_CACHE_FILE)
    glue_cache = load_cache(GLUE_CACHE_FILE)
    datasync_cache = load_cache(DATASYNC_CACHE_FILE)
    kinesis_cache = load_cache(KINESIS_CACHE_FILE)
    elb_cache = load_cache(ELB_CACHE_FILE)
    route53_cache = load_cache(ROUTE53_CACHE_FILE)
    waf_cache = load_cache(WAF_CACHE_FILE)
    apigw_cache = load_cache(APIGW_CACHE_FILE)
    appsync_cache = load_cache(APPSYNC_CACHE_FILE)
    sagemaker_cache = load_cache(SAGEMAKER_CACHE_FILE)
    fsx_cache = load_cache(FSX_CACHE_FILE)
    workspaces_cache = load_cache(WORKSPACES_CACHE_FILE)
    backup_cache = load_cache(BACKUP_CACHE_FILE)
    directconnect_cache = load_cache(DIRECTCONNECT_CACHE_FILE)
    stepfunctions_cache = load_cache(STEPFUNCTIONS_CACHE_FILE)
    lightsail_cache = load_cache(LIGHTSAIL_CACHE_FILE)
    cloudtrail_cache = load_cache(CLOUDTRAIL_CACHE_FILE)

    regions = [
        "us-west-2", "us-west-1", "us-east-1", "us-east-2",
        "eu-west-2", "ap-southeast-1", "ap-east-1"
    ]

    # Fetch org accounts
    all_accounts = []
    paginator = org_client.get_paginator("list_accounts")
    for page in paginator.paginate():
        all_accounts.extend(page["Accounts"])

    # Filter by environment
    target_ids = filter_accounts(env)
    accounts_to_scan = []
    for acct in all_accounts:
        if acct["Id"] in target_ids:
            if acct["Id"] in PROD_ACCOUNTS:
                acct["Env"] = "prod"
            elif acct["Id"] in DEV_ACCOUNTS:
                acct["Env"] = "dev"
            elif acct["Id"] in UAT_ACCOUNTS:
                acct["Env"] = "uat"
            accounts_to_scan.append(acct)

    print(f"\n✅ Scanning {len(accounts_to_scan)} accounts across {len(regions)} regions...\n")

    # ---------- ECS Scan ----------
    ecs_results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_ecs_for_account, acct, master_session, regions, ecs_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="ECS Scan"):
            ecs_results.extend(f.result())

    save_cache(ECS_CACHE_FILE, ecs_cache)

    # ---------- EC2 Scan ----------
    ec2_results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_ec2_for_account, acct, master_session, regions, ec2_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="EC2 Scan"):
            ec2_results.extend(f.result())

    save_cache(EC2_CACHE_FILE, ec2_cache)

    # ---------- EBS Scan ----------
    ebs_cache = load_cache(EBS_CACHE_FILE)
    ebs_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_ebs_for_account, acct, master_session, regions, ebs_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="EBS Scan"):
            ebs_results.extend(f.result())

    save_cache(EBS_CACHE_FILE, ebs_cache)

    # ---------- RDS Scan ----------
    rds_cache = load_cache(RDS_CACHE_FILE)
    rds_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_rds_for_account, acct, master_session, regions, rds_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="RDS Scan"):
            rds_results.extend(f.result())

    save_cache(RDS_CACHE_FILE, rds_cache)

    # ---------- Lambda Scan ----------
    lambda_cache = load_cache(LAMBDA_CACHE_FILE)
    lambda_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_lambda_for_account, acct, master_session, regions, lambda_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="Lambda Scan"):
            lambda_results.extend(f.result())

    save_cache(LAMBDA_CACHE_FILE, lambda_cache)

    # ---------- ECR Scan ----------
    ecr_cache = load_cache(ECR_CACHE_FILE)
    ecr_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_ecr_for_account, acct, master_session, regions, ecr_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="ECR Scan"):
            ecr_results.extend(f.result())

    save_cache(ECR_CACHE_FILE, ecr_cache)

    # ---------- S3 Scan ----------
    s3_cache = load_cache(S3_CACHE_FILE)
    s3_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_s3_for_account, acct, master_session, s3_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="S3 Scan"):
            s3_results.extend(f.result())

    save_cache(S3_CACHE_FILE, s3_cache)

    # ---------- CloudWatch Scan ----------
    cw_cache = load_cache(CLOUDWATCH_CACHE_FILE)
    cloudwatch_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_cloudwatch_for_account, acct, master_session, regions, cw_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="CloudWatch Scan"):
            cloudwatch_results.extend(f.result())

    save_cache(CLOUDWATCH_CACHE_FILE, cw_cache)

    # ---------- VPC Scan ----------
    vpc_results = []
    vpc_cache = load_cache(VPC_CACHE_FILE)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_vpc_for_account, acct, master_session, regions, vpc_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="VPC Scan"):
            vpc_results.extend(f.result())

    save_cache(VPC_CACHE_FILE, vpc_cache)

    # ---------- SecurityHub Scan ----------
    securityhub_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_securityhub_for_account, acct, master_session, regions, sh_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="SecurityHub Scan"):
            securityhub_results.extend(f.result())

    save_cache(SECURITYHUB_CACHE_FILE, sh_cache)

    # ---------- GuardDuty Scan ----------
    guardduty_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_guardduty_for_account, acct, master_session, regions, gd_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="GuardDuty Scan"):
            guardduty_results.extend(f.result())

    save_cache(GUARDDUTY_CACHE_FILE, gd_cache)

    # ---------- Inspector Scan ----------
    inspector_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_inspector_for_account, acct, master_session, regions, inspector_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="Inspector Scan"):
            inspector_results.extend(f.result())

    save_cache(INSPECTOR_CACHE_FILE, inspector_cache)


    # ---------- Macie Scan ----------
    macie_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_macie_for_account, acct, master_session, regions, macie_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="Macie Scan"):
            macie_results.extend(f.result())

    save_cache(MACIE_CACHE_FILE, macie_cache)

    # ---------- AWS Config Scan ----------
    config_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_config_for_account, acct, master_session, regions, config_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="Config Scan"):
            config_results.extend(f.result())

    save_cache(CONFIG_CACHE_FILE, config_cache)

    # ---------- IAM Scan ----------
    iam_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_iam_for_account, acct, master_session, iam_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="IAM Scan"):
            iam_results.extend(f.result())

    save_cache(IAM_CACHE_FILE, iam_cache)

    # ---------- KMS Scan ----------
    kms_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_kms_for_account, acct, master_session, regions, kms_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="KMS Scan"):
            kms_results.extend(f.result())

    save_cache(KMS_CACHE_FILE, kms_cache)

    # ---------- DynamoDB Scan ----------
    dynamodb_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_dynamodb_for_account, acct, master_session, regions, dynamodb_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="DynamoDB Scan"):
            dynamodb_results.extend(f.result())

    save_cache(DYNAMODB_CACHE_FILE, dynamodb_cache)


    # ---------- Glue Scan ----------
    glue_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_glue_for_account, acct, master_session, regions, glue_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="Glue Scan"):
            glue_results.extend(f.result())

    save_cache(GLUE_CACHE_FILE, glue_cache)

    # ---------- DataSync Scan ----------
    datasync_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_datasync_for_account, acct, master_session, regions, datasync_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="DataSync Scan"):
            datasync_results.extend(f.result())

    save_cache(DATASYNC_CACHE_FILE, datasync_cache)

    # ---------- Kinesis Scan ----------
    kinesis_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_kinesis_for_account, acct, master_session, regions, kinesis_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="Kinesis Scan"):
            kinesis_results.extend(f.result())

    save_cache(KINESIS_CACHE_FILE, kinesis_cache)

    # ---------- ELB Scan ----------
    elb_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_elb_for_account, acct, master_session, regions, elb_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="ELB Scan"):
            elb_results.extend(f.result())

    save_cache(ELB_CACHE_FILE, elb_cache)

    # ---------- Route53 Scan ----------
    route53_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_route53_for_account, acct, master_session, route53_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="Route53 Scan"):
            route53_results.extend(f.result())

    save_cache(ROUTE53_CACHE_FILE, route53_cache)

    # ---------- WAF Scan ----------
    waf_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_waf_for_account, acct, master_session, regions, waf_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="WAF Scan"):
            waf_results.extend(f.result())

    save_cache(WAF_CACHE_FILE, waf_cache)

    # ---------- API Gateway Scan ----------
    apigw_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_apigateway_for_account, acct, master_session, regions, apigw_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="API Gateway Scan"):
            apigw_results.extend(f.result())

    save_cache(APIGW_CACHE_FILE, apigw_cache)

    # ---------- AppSync Scan ----------
    appsync_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_appsync_for_account, acct, master_session, regions, appsync_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="AppSync Scan"):
            appsync_results.extend(f.result())

    save_cache(APPSYNC_CACHE_FILE, appsync_cache)

    # ---------- SageMaker Scan ----------
    sagemaker_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_sagemaker_for_account, acct, master_session, regions, sagemaker_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="SageMaker Scan"):
            sagemaker_results.extend(f.result())

    save_cache(SAGEMAKER_CACHE_FILE, sagemaker_cache)

    # ---------- FSx Scan ----------
    fsx_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_fsx_for_account, acct, master_session, regions, fsx_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="FSx Scan"):
            fsx_results.extend(f.result())

    save_cache(FSX_CACHE_FILE, fsx_cache)

        # ---------- WorkSpaces Scan ----------
    workspaces_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_workspaces_for_account, acct, master_session, regions, workspaces_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="WorkSpaces Scan"):
            workspaces_results.extend(f.result())

    save_cache(WORKSPACES_CACHE_FILE, workspaces_cache)

    # ---------- AWS Backup Scan ----------
    backup_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_backup_for_account, acct, master_session, regions, backup_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="AWS Backup Scan"):
            backup_results.extend(f.result())

    save_cache(BACKUP_CACHE_FILE, backup_cache)

    # ---------- Direct Connect Scan ----------
    directconnect_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_directconnect_for_account, acct, master_session, regions, directconnect_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="Direct Connect Scan"):
            directconnect_results.extend(f.result())

    save_cache(DIRECTCONNECT_CACHE_FILE, directconnect_cache)

    # ---------- Step Functions Scan ----------
    stepfunctions_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_stepfunctions_for_account, acct, master_session, regions, stepfunctions_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="Step Functions Scan"):
            stepfunctions_results.extend(f.result())

    save_cache(STEPFUNCTIONS_CACHE_FILE, stepfunctions_cache)

    # ---------- Lightsail Scan ----------
    lightsail_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_lightsail_for_account, acct, master_session, regions, lightsail_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="Lightsail Scan"):
            lightsail_results.extend(f.result())

    save_cache(LIGHTSAIL_CACHE_FILE, lightsail_cache)

    # ---------- CloudTrail Scan ----------
    cloudtrail_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(find_cloudtrail_for_account, acct, master_session, regions, cloudtrail_cache)
            for acct in accounts_to_scan
        ]
        for f in tqdm(as_completed(futures), total=len(futures), desc="CloudTrail Scan"):
            cloudtrail_results.extend(f.result())

    save_cache(CLOUDTRAIL_CACHE_FILE, cloudtrail_cache)

    # ---------- Write Excel ----------
    ecs_df = strip_timezone(pd.DataFrame(ecs_results))
    ec2_df = strip_timezone(pd.DataFrame(ec2_results))
    ebs_df = strip_timezone(pd.DataFrame(ebs_results))
    rds_df = strip_timezone(pd.DataFrame(rds_results))
    lambda_df = strip_timezone(pd.DataFrame(lambda_results))
    ecr_df = strip_timezone(pd.DataFrame(ecr_results))
    s3_df = strip_timezone(pd.DataFrame(s3_results))
    cloudwatch_df = strip_timezone(pd.DataFrame(cloudwatch_results))
    vpc_df = strip_timezone(pd.DataFrame(vpc_results))
    securityhub_df = strip_timezone(pd.DataFrame(securityhub_results))
    guardduty_df = strip_timezone(pd.DataFrame(guardduty_results))
    inspector_df = strip_timezone(pd.DataFrame(inspector_results))
    macie_df = strip_timezone(pd.DataFrame(macie_results))
    config_df = strip_timezone(pd.DataFrame(config_results))
    iam_df = strip_timezone(pd.DataFrame(iam_results))
    kms_df = strip_timezone(pd.DataFrame(kms_results))
    dynamodb_df = strip_timezone(pd.DataFrame(dynamodb_results))
    glue_df = strip_timezone(pd.DataFrame(glue_results))
    datasync_df = strip_timezone(pd.DataFrame(datasync_results))
    kinesis_df = strip_timezone(pd.DataFrame(kinesis_results))
    elb_df = strip_timezone(pd.DataFrame(elb_results))
    route53_df = strip_timezone(pd.DataFrame(route53_results))
    waf_df = strip_timezone(pd.DataFrame(waf_results))
    apigw_df = strip_timezone(pd.DataFrame(apigw_results))
    appsync_df = strip_timezone(pd.DataFrame(appsync_results))
    sagemaker_df = strip_timezone(pd.DataFrame(sagemaker_results))
    fsx_df = strip_timezone(pd.DataFrame(fsx_results))
    workspaces_df = strip_timezone(pd.DataFrame(workspaces_results))
    backup_df = strip_timezone(pd.DataFrame(backup_results))
    directconnect_df = strip_timezone(pd.DataFrame(directconnect_results))
    stepfunctions_df = strip_timezone(pd.DataFrame(stepfunctions_results))
    lightsail_df = strip_timezone(pd.DataFrame(lightsail_results))
    cloudtrail_df = strip_timezone(pd.DataFrame(cloudtrail_results))

    out_file = "AWS_Inventory_Report-AllRegions.xlsx"
    with pd.ExcelWriter(out_file) as writer:
        ecs_df.to_excel(writer, sheet_name="Cluster Details", index=False)
        ec2_df.to_excel(writer, sheet_name="EC2 Details", index=False)
        ebs_df.to_excel(writer, sheet_name="EBS Details", index=False)
        rds_df.to_excel(writer, sheet_name="RDS Details", index=False)
        lambda_df.to_excel(writer, sheet_name="Lambda Details", index=False)
        ecr_df.to_excel(writer, sheet_name="ECR Details", index=False)
        s3_df.to_excel(writer, sheet_name="S3 Details", index=False)
        cloudwatch_df.to_excel(writer, sheet_name="CloudWatch Details", index=False)
        vpc_df.to_excel(writer, sheet_name="VPC Details", index=False)
        securityhub_df.to_excel(writer, sheet_name="SecurityHub Details", index=False)
        guardduty_df.to_excel(writer, sheet_name="GuardDuty Details", index=False)
        inspector_df.to_excel(writer, sheet_name="Inspector Details", index=False)
        macie_df.to_excel(writer, sheet_name="Macie Details", index=False)
        config_df.to_excel(writer, sheet_name="Config Details", index=False)
        iam_df.to_excel(writer, sheet_name="IAM Details", index=False)
        kms_df.to_excel(writer, sheet_name="KMS Details", index=False)
        dynamodb_df.to_excel(writer, sheet_name="DynamoDB Details", index=False)
        glue_df.to_excel(writer, sheet_name="Glue Details", index=False)
        datasync_df.to_excel(writer, sheet_name="DataSync Details", index=False)
        kinesis_df.to_excel(writer, sheet_name="Kinesis Details", index=False)
        elb_df.to_excel(writer, sheet_name="ELB Details", index=False)
        route53_df.to_excel(writer, sheet_name="Route53 Details", index=False)
        waf_df.to_excel(writer, sheet_name="WAF Details", index=False)
        apigw_df.to_excel(writer, sheet_name="API Gateway Details", index=False)
        appsync_df.to_excel(writer, sheet_name="AppSync Details", index=False)
        sagemaker_df.to_excel(writer, sheet_name="SageMaker Details", index=False)
        fsx_df.to_excel(writer, sheet_name="FSx Details", index=False)
        workspaces_df.to_excel(writer, sheet_name="WorkSpaces Details", index=False)
        backup_df.to_excel(writer, sheet_name="AWS Backup Details", index=False)
        directconnect_df.to_excel(writer, sheet_name="Direct Connect Details", index=False)
        stepfunctions_df.to_excel(writer, sheet_name="Step Functions Details", index=False)
        lightsail_df.to_excel(writer, sheet_name="Lightsail Details", index=False)
        cloudtrail_df.to_excel(writer, sheet_name="CloudTrail Details", index=False)

    print("\n✅ Inventory report generated:", out_file)
    print(f"✅ ECS Clusters: {len(ecs_df)}")
    print(f"✅ EC2 Instances: {len(ec2_df)}")
    print(f"✅ EBS Volumes: {len(ebs_df)}")
    print(f"✅ RDS Instances: {len(rds_df)}")
    print(f"✅ Lambda Functions: {len(lambda_df)}")
    print(f"✅ ECR Repositories: {len(ecr_df)}")
    print(f"✅ S3 Buckets: {len(s3_df)}")
    print(f"✅ CloudWatch Regions Scanned: {len(cloudwatch_df)}")
    print(f"✅ VPCs: {len(vpc_df)}")
    print(f"✅ SecurityHub Regions Scanned: {len(securityhub_df)}")
    print(f"✅ GuardDuty Regions Scanned: {len(guardduty_df)}")
    print(f"✅ Inspector Regions Scanned: {len(inspector_df)}")
    print(f"✅ Macie Regions Scanned: {len(macie_df)}")
    print(f"✅ AWS Config Regions Scanned: {len(config_df)}")
    print(f"✅ IAM Accounts Scanned: {len(iam_df)}")
    print(f"✅ KMS Keys: {len(kms_df)}")
    print(f"✅ DynamoDB Tables: {len(dynamodb_df)}")
    print(f"✅ Glue Jobs: {len(glue_df)}")
    print(f"✅ DataSync Tasks: {len(datasync_df)}")
    print(f"✅ Kinesis Streams: {len(kinesis_df)}")
    print(f"✅ Load Balancers: {len(elb_df)}")
    print(f"✅ Route53 Hosted Zones: {len(route53_df)}")
    print(f"✅ WAF WebACLs: {len(waf_df)}")
    print(f"✅ API Gateways: {len(apigw_df)}")
    print(f"✅ AppSync APIs: {len(appsync_df)}")
    print(f"✅ SageMaker Notebooks: {len(sagemaker_df)}")
    print(f"✅ FSx File Systems: {len(fsx_df)}")
    print(f"✅ WorkSpaces: {len(workspaces_df)}")
    print(f"✅ AWS Backup Vaults: {len(backup_df)}")
    print(f"✅ Direct Connect Connections: {len(directconnect_df)}")
    print(f"✅ Step Functions: {len(stepfunctions_df)}")
    print(f"✅ Lightsail Instances: {len(lightsail_df)}")
    print(f"✅ CloudTrail Trails: {len(cloudtrail_df)}")

if __name__ == "__main__":
    main()
