#!/usr/bin/env python3
"""
Enhanced AWS ECS inventory script with:
- Environment selection (dev/prod/uat/all)
- Concurrency for faster scans
- Progress bars (tqdm)
- Local caching to skip unchanged accounts
- Single Excel output (Cluster Details only)
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

import boto3
import pandas as pd
from botocore.exceptions import ClientError
from tqdm import tqdm

CACHE_FILE = "ecs_cache.json"
CACHE_TTL_HOURS = 24
REPORT_FILE_NAME = "AWS_ECS_Report-AllRegions.xlsx"


PROD_ACCOUNTS = [
    "123456789012", "123456789012", "123456789012", "123456789012",
    "123456789012", "123456789012", "123456789012", "123456789012",
    "123456789012", "123456789012", "123456789012", "123456789012",
    "123456789012", "123456789012", "123456789012", "123456789012",
    "123456789012", "123456789012", "123456789012", "123456789012",
    "123456789012", "123456789012", "123456789012", "123456789012",
    "123456789012", "123456789012", "123456789012", "123456789012",
    "123456789012", "123456789012", "123456789012", "123456789012",
    "123456789012", "123456789012", "123456789012"
]

DEV_ACCOUNTS = [
    "123456789012", "123456789012", "123456789012", "123456789012",
    "123456789012", "123456789012", "123456789012", "123456789012",
    "123456789012", "123456789012", "123456789012", "123456789012",
    "123456789012", "123456789012", "123456789012", "123456789012",
    "123456789012", "123456789012", "123456789012", "123456789012",
    "123456789012", "123456789012", "123456789012"
]

UAT_ACCOUNTS = [
    "123456789012", "123456789012", "123456789012", "123456789012",
    "123456789012", "123456789012", "123456789012", "123456789012",
    "123456789012", "123456789012", "123456789012", "123456789012",
    "123456789012", "123456789012", "123456789012"
]


def load_cache():
    """Load ECS results cache from disk."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as cache_file:
            return json.load(cache_file)
    return {}


def save_cache(cache_contents):
    """Write ECS cache to disk."""
    with open(CACHE_FILE, "w", encoding="utf-8") as cache_file:
        json.dump(cache_contents, cache_file, indent=2)


def is_cache_valid(account_id, cache_contents):
    """Check if cached data for an account is still fresh."""
    entry = cache_contents.get(account_id)
    if not entry:
        return False

    last_run = datetime.fromisoformat(entry["timestamp"])
    return datetime.now() - last_run < timedelta(hours=CACHE_TTL_HOURS)


def get_service_task_definitions(ecs_client, cluster_arn, service_arn):
    """Return task definition details for an ECS service."""
    try:
        svc_desc = ecs_client.describe_services(
            cluster=cluster_arn,
            services=[service_arn]
        )
        services = svc_desc.get("services")
        if not services:
            return []

        tdef_arn = services[0].get("taskDefinition")
        if not tdef_arn:
            return []

        tdef_desc = ecs_client.describe_task_definition(
            taskDefinition=tdef_arn
        )
        task_def = tdef_desc.get("taskDefinition")
        if not task_def:
            return []

        return [{
            "family": task_def.get("family"),
            "revision": task_def.get("revision"),
            "taskDefinitionArn": task_def.get("taskDefinitionArn"),
            "status": task_def.get("status"),
            "cpu": task_def.get("cpu"),
            "memory": task_def.get("memory"),
            "networkMode": task_def.get("networkMode"),
            "requiresCompatibilities": task_def.get("requiresCompatibilities", []),
        }]

    except ClientError:
        return []


def get_cluster_services(ecs_client, cluster_arn):
    """Return ECS service details for all services in a cluster."""
    try:
        svc_arns = []
        svc_paginator = ecs_client.get_paginator("list_services")
        for svc_page in svc_paginator.paginate(cluster=cluster_arn):
            svc_arns.extend(svc_page.get("serviceArns", []))

        services = []
        for idx in range(0, len(svc_arns), 10):
            batch = svc_arns[idx:idx + 10]
            desc = ecs_client.describe_services(
                cluster=cluster_arn,
                services=batch
            )
            for svc in desc.get("services", []):
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
        return services

    except ClientError:
        return []


def assume_role(account_id, base_session):
    """Assume OrganizationAccountAccessRole into the given account."""
    try:
        sts_client = base_session.client("sts")
        resp = sts_client.assume_role(
            RoleArn=f"arn:aws:iam::{account_id}:role/OrganizationAccountAccessRole",
            RoleSessionName="ECSClusterInventory"
        )
        creds = resp["Credentials"]
        return boto3.Session(
            aws_access_key_id=creds["AccessKeyId"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds["SessionToken"]
        )
    except ClientError:
        return None


def build_cluster_record(cluster, region, account_info, ecs_client):
    """Build a cleaned record from cluster data."""
    services = get_cluster_services(ecs_client, cluster["clusterArn"])
    task_defs = []
    for svc in services:
        svc_arn = svc.get("serviceArn")
        task_defs.extend(
            get_service_task_definitions(
                ecs_client,
                cluster["clusterArn"],
                svc_arn
            )
        )

    tag_dict = {
        tag["key"]: tag.get("value", "") for tag in cluster.get("tags", [])
    }

    return {
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
        "Account ID": account_info["Id"],
        "Account Name": account_info["Name"],
        "Environment": account_info["Env"],
        "Tags": str(tag_dict),
        "Services": str(services),
        "Task Definitions": str(task_defs)
    }


def process_region(session_obj, region, account_info):
    """Return ECS cluster detail dictionaries for a single region."""
    try:
        ecs_client = session_obj.client("ecs", region_name=region)

        cluster_arns = []
        cluster_paginator = ecs_client.get_paginator("list_clusters")
        for cluster_page in cluster_paginator.paginate():
            cluster_arns.extend(cluster_page.get("clusterArns", []))

        records = []
        for idx in range(0, len(cluster_arns), 100):
            batch = cluster_arns[idx:idx + 100]
            desc = ecs_client.describe_clusters(
                clusters=batch,
                include=["TAGS"]
            )

            for cluster in desc.get("clusters", []):
                record = build_cluster_record(
                    cluster, region, account_info, ecs_client
                )
                records.append(record)

        return records

    except ClientError:
        return []


def find_ecs_clusters_for_account(account_info, root_session, region_list, cache_contents):
    """Scan ECS clusters for a given AWS account across regions."""
    account_id = account_info["Id"]

    if is_cache_valid(account_id, cache_contents):
        return cache_contents[account_id]["data"]

    if account_id == cache_contents.get("master_account_id"):
        session_obj = root_session
    else:
        session_obj = assume_role(account_id, root_session)

    if not session_obj:
        return []

    results = []
    for region in region_list:
        results.extend(
            process_region(session_obj, region, account_info)
        )

    cache_contents[account_id] = {
        "timestamp": datetime.now().isoformat(),
        "data": results
    }

    return results


def filter_accounts(env_name):
    """Return account IDs for selected environment."""
    if env_name == "prod":
        return PROD_ACCOUNTS
    if env_name == "dev":
        return DEV_ACCOUNTS
    if env_name == "uat":
        return UAT_ACCOUNTS
    return PROD_ACCOUNTS + DEV_ACCOUNTS + UAT_ACCOUNTS


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--profile_name", required=True, help="AWS profile name")
    parser.add_argument(
        "-e", "--env",
        required=True,
        choices=["dev", "prod", "uat", "all"],
        help="Environment to scan"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    aws_profile = args.profile_name
    env_selected = args.env

    master_session = boto3.Session(profile_name=aws_profile)
    org_client = master_session.client("organizations")

    cache_data = load_cache()

    regions = [
        "us-west-2", "us-east-1", "us-east-2",
        "eu-west-2", "ap-southeast-1",
        "ap-east-1", "us-west-1"
    ]

    accounts = []
    acct_paginator = org_client.get_paginator("list_accounts")
    for acct_page in acct_paginator.paginate():
        accounts.extend(acct_page.get("Accounts", []))

    wanted_ids = filter_accounts(env_selected)

    scanned_accounts = []
    for acct in accounts:
        acct_id = acct["Id"]
        if acct_id in wanted_ids:
            acct["Env"] = (
                "prod" if acct_id in PROD_ACCOUNTS else
                "dev" if acct_id in DEV_ACCOUNTS else
                "uat"
            )
            scanned_accounts.append(acct)

    print(f"\n✅ Scanning {len(scanned_accounts)} accounts across {len(regions)} regions...\n")

    collected = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(
                find_ecs_clusters_for_account,
                acct,
                master_session,
                regions,
                cache_data
            ): acct
            for acct in scanned_accounts
        }

        for future in tqdm(as_completed(futures), total=len(futures), desc="Scanning Accounts"):
            result = future.result()
            if isinstance(result, list):
                collected.extend(result)

    save_cache(cache_data)

    df = pd.DataFrame(collected)

    if df.empty:
        print("\n⚠ No ECS clusters found — building empty report.")
        df = pd.DataFrame(columns=[
            "Cluster ARN", "Cluster Name", "Status",
            "Running Tasks Count", "Pending Tasks Count",
            "Registered Container Instances Count",
            "Active Services Count", "Region",
            "Account ID", "Account Name",
            "Environment", "Tags", "Services",
            "Task Definitions"
        ])

    with pd.ExcelWriter(REPORT_FILE_NAME) as writer:
        df.to_excel(writer, sheet_name="Cluster Details", index=False)

    print(f"\n✅ Report written: {REPORT_FILE_NAME}")
    print(f"✅ Total clusters found: {len(df)}")
    print("✅ Scan complete.\n")
