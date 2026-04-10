"""
This script retrieves Inspector findings from a Security Tooling account,
aggregates them, and generates a styled PDF report.
"""

import argparse
from datetime import datetime

import boto3
import botocore.exceptions
import pdfkit

def get_inspector_findings(profile_name, regions_list):
    """
    Retrieves all Inspector findings from the Security Tooling account across multiple regions.

    Args:
        profile_name (str): The name of the AWS profile to use.
        regions_list (list): List of AWS regions to query.

    Returns:
        list: A list of Inspector findings.
    """
    all_findings = []
    session = boto3.Session(profile_name=profile_name)
    for region in regions_list:
        try:
            inspector = session.client("inspector2", region_name=region)
            paginator = inspector.get_paginator("list_findings")
            for page in paginator.paginate():
                all_findings.extend(page["findings"])
        except botocore.exceptions.ClientError as ex:
            if ex.response["Error"]["Code"] == "AccessDeniedException":
                print(f"Skipping region {region}: Access denied.")
            else:
                print(f"Error fetching Inspector findings in {region}: {ex}")
    return all_findings

def process_findings(findings_list):
    """
    Processes and aggregates Inspector findings.

    Args:
        findings_list (list): A list of Inspector findings.

    Returns:
        dict: A dictionary containing aggregated data.
    """

    aggregated_data = {
        "Severity": {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
            "INFORMATIONAL": 0,
            "UNTRIAGED": 0
        },
        "Account": {},  # Count occurrences per account
        "Region": {},   # Count occurrences per region
    }

    for finding in findings_list:
        severity = finding["severity"]
        aggregated_data["Severity"][severity] += 1

        account_id = finding["awsAccountId"]
        aggregated_data["Account"][account_id] = aggregated_data["Account"].get(account_id, 0) + 1

        region = finding["findingArn"].split(":")[3]
        aggregated_data["Region"][region] = aggregated_data["Region"].get(region, 0) + 1

    return aggregated_data

def get_account_name(account_id, profile_name, region="us-west-2"):
    """
    Retrieves the account name from AWS Organizations.

    Args:
        account_id (str): The ID of the AWS account.
        profile_name (str): The name of the AWS profile to use.
        region (str): The AWS region. Defaults to 'us-west-2'.

    Returns:
        str: The name of the account, or "Unknown" if not found.
    """
    try:
        session = boto3.Session(profile_name=profile_name)
        org_client = session.client("organizations", region_name=region)
        response = org_client.describe_account(AccountId=account_id)
        return response["Account"]["Name"]
    except botocore.exceptions.ClientError as ex:
        print(f"Error fetching account name for {account_id}: {ex}")
        return "Unknown"

def generate_pdf_report(aggregated_data_report, total_findings, profile_name):
    """Generates a PDF report from the aggregated Inspector data."""

    now = datetime.now()
    date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")

    # CSS for styling the report
    css = """
    body {
        font-family: sans-serif;
    }
    h1, h2 {
        color: #333;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 20px;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    th {
        background-color: #f0f0f0;
    }
    ul {
        list-style-type: disc;
        margin-left: 20px;
    }
    """

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Inspector Findings Report</title>
        <style>{css}</style>  </head>
    <body>
        <h1>Inspector Findings Summary</h1>
        <p>Total Findings: {total_findings}</p>
        <p>Report Generated: {date_time_str}</p>

        <h2>Severity Breakdown</h2>
        <table>
            <thead>
                <tr>
                    <th>Severity</th>
                    <th>Count</th>
                    <th>Percentage</th>
                </tr>
            </thead>
            <tbody>"""

    for severity, count in aggregated_data_report["Severity"].items():
        percentage = (count / total_findings) * 100
        html += f"""
                <tr>
                    <td>{severity}</td>
                    <td>{count}</td>
                    <td>{percentage:.1f}%</td>
                </tr>"""

    html += """
            </tbody>
        </table>

        <h2>Findings by Account</h2>
        <ul>"""

    sorted_accounts = sorted(
        aggregated_data_report["Account"].items(),
        key=lambda item: item[1],
        reverse=True
    )

    for account_id, count in sorted_accounts:
        account_name = get_account_name(account_id, profile_name)
        html += f"<li>{account_name} ({account_id}): {count}</li>"

    html += """
        </ul>

        <h2>Findings by Region</h2>
        <ul>"""

    for region, count in aggregated_data_report["Region"].items():
        html += f"<li>{region}: {count}</li>"

    html += """
        </ul>
    </body>
    </html>
    """
    return html

def get_all_regions(profile_name):
    """Retrieves all available AWS regions."""
    session = boto3.Session(profile_name=profile_name)
    ec2 = session.client("ec2")
    return [region["RegionName"] for region in ec2.describe_regions()["Regions"]]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Retrieve and aggregate Inspector findings from Security Tooling account."
    )
    parser.add_argument(
        "--profile", required=True, help="AWS profile name for the Security Tooling account"
    )
    parser.add_argument(
        "--region", default="us-west-2", help=("AWS region (default: us-west-2). "
                                              "Use 'all' to query all regions.")
    )
    parser.add_argument("--all-regions", action="store_true", help="If set, query all regions")
    args = parser.parse_args()

    if args.all_regions:
        regions_to_query = get_all_regions(args.profile)
    else:
        regions_to_query = [args.region]

    inspector_findings = get_inspector_findings(args.profile, regions_to_query)

    if inspector_findings:
        aggregated_data = process_findings(inspector_findings)
        TOTAL_FINDINGS = len(inspector_findings)

        # Generate HTML content
        html_report = generate_pdf_report(aggregated_data, TOTAL_FINDINGS, args.profile)

        right_now = datetime.now()
        date_time_stamp = right_now.strftime("%Y%m%d_%H%M%S")

        if args.all_regions:
            filename = f"inspector_findings_report_all-regions_{date_time_stamp}.pdf"
        else:
            filename = f"inspector_findings_report_{args.region}_{date_time_stamp}.pdf"

        # Convert HTML to PDF using pdfkit
        pdfkit.from_string(html_report, filename)

        print(f"\nReport generated: {filename}")
