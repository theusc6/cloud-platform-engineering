""" 
AWS Organization Region Analyzer

This script analyzes Service Control Policies (SCPs) in an AWS Organization to identify
all regions referenced in aws:RequestedRegion conditions. It helps identify which 
regions are being controlled or restricted across the organization's SCPs.

The script:
- Retrieves all SCPs in the organization
- Extracts aws:RequestedRegion values from each SCP
- Aggregates and displays unique regions in a sorted list

Requirements:
    - boto3
    - Valid AWS credentials with Organizations access
    - AWS CLI profile configured

Usage:
    python script.py --profile <aws-profile-name>

Example:
    python script.py --profile myorg-master

    Prints a sorted list of all unique AWS regions found in SCP conditions
"""

import argparse
import json
import boto3

def get_scp_ids(org_client):
    """
    Retrieve all Service Control Policy (SCP) IDs in the organization.

    Args:
        org_client (boto3.client): The Boto3 Organizations client.

    Returns:
        list: A list of SCP IDs.
    """
    scp_ids = []
    paginator = org_client.get_paginator("list_policies")
    for page in paginator.paginate(Filter="SERVICE_CONTROL_POLICY"):
        for policy in page["Policies"]:
            scp_ids.append(policy["Id"])
    return scp_ids

def get_requested_regions(org_client, scp_id):
    """
    Extract aws:RequestedRegion values from a specific SCP.

    Args:
        org_client (boto3.client): The Boto3 Organizations client.
        scp_id (str): The ID of the SCP to analyze.

    Returns:
        set: A set of regions found in the SCP's aws:RequestedRegion conditions.
    """
    response = org_client.describe_policy(PolicyId=scp_id)
    policy_content = response["Policy"]["Content"]
    policy_json = json.loads(policy_content)  # Parse the JSON string
    regions = set()

    # Iterate through statements to find aws:RequestedRegion
    for statement in policy_json.get("Statement", []):
        condition = statement.get("Condition", {})
        if "StringEquals" in condition and "aws:RequestedRegion" in condition["StringEquals"]:
            regions.update(condition["StringEquals"]["aws:RequestedRegion"])
        if "StringNotEquals" in condition and "aws:RequestedRegion" in condition["StringNotEquals"]:
            regions.update(condition["StringNotEquals"]["aws:RequestedRegion"])
    return regions

def main():
    """
    Main function to aggregate and display regions from SCPs.

    This function retrieves all SCPs in the organization, extracts
    aws:RequestedRegion values, and displays the unique regions in a sorted list.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Retrieve aws:RequestedRegion values from SCPs in an AWS organization."
    )
    parser.add_argument(
        "--profile",
        required=True,
        help="The AWS CLI profile to use for authentication (e.g., myorg-master)."
    )
    args = parser.parse_args()

    # Initialize the AWS Organizations client
    session = boto3.Session(profile_name=args.profile)
    org_client = session.client("organizations")

    all_regions = set()
    scp_ids = get_scp_ids(org_client)

    print(f"Found {len(scp_ids)} SCPs. Processing...")
    for scp_id in scp_ids:
        print(f"Processing SCP ID: {scp_id}")
        regions = get_requested_regions(org_client, scp_id)
        all_regions.update(regions)

    # Sort and display unique regions
    sorted_regions = sorted(all_regions)
    print("\nRegions found in aws:RequestedRegion:")
    print("------------------")
    for region in sorted_regions:
        print(region)
    print("------------------")

if __name__ == "__main__":
    main()
