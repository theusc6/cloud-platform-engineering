"""
This script retrieves security findings from AWS Security Hub,
aggregates them, and generates a styled PDF report.
"""

import argparse
from datetime import datetime

import boto3
import botocore.exceptions
import pdfkit

def get_security_findings(profile_name, home_region="us-west-2"):
    """
    Retrieves all security findings from AWS Security Hub.

    Args:
        profile_name (str): The name of the AWS profile to use for authentication.
        home_region (str): The AWS region where Security Hub is configured.
                           Defaults to 'us-west-2'.

    Returns:
        list: A list of security findings, or None if an error occurs.
    """

    session = boto3.Session(profile_name=profile_name)
    securityhub = session.client("securityhub", region_name=home_region)

    try:
        findings = []
        paginator = securityhub.get_paginator("get_findings")
        for page in paginator.paginate():
            findings.extend(page["Findings"])
        return findings

    except botocore.exceptions.ClientError as ex:
        print(f"Error fetching findings: {ex}")
        return None

def process_findings(findings_list):
    """
    Normalizes and aggregates security findings.

    Args:
        findings_list (list): A list of security findings from Security Hub.

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
        },
        "ComplianceStatus": {
            "PASSED": 0,
            "FAILED": 0,
            "WARNING": 0,
            "NOT_AVAILABLE": 0,
        },
        "ResourceType": {},  # Count occurrences of each resource type
        "Service": {},  # Count occurrences for each AWS service
        "Region": {},  # Count occurrences per region
    }

    for finding in findings_list:
        severity_label = finding["Severity"]["Label"]
        aggregated_data["Severity"][severity_label] += 1

        if "Compliance" in finding:
            aggregated_data["ComplianceStatus"][finding["Compliance"]["Status"]] += 1

        resource_type = finding["Resources"][0]["Type"]
        aggregated_data["ResourceType"][resource_type] = (
            aggregated_data["ResourceType"].get(resource_type, 0) + 1
        )

        service = finding["ProductArn"].split(":")[5].split("/")[1]
        aggregated_data["Service"][service] = (
            aggregated_data["Service"].get(service, 0) + 1
        )

        region = finding["ProductArn"].split(":")[3]
        aggregated_data["Region"][region] = (
            aggregated_data["Region"].get(region, 0) + 1
        )

    return aggregated_data

def generate_pdf_report(aggregated_data_report, total_findings):
    """Generates a PDF report from the aggregated Security Hub data."""

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
        <title>Security Hub Findings Report</title>
        <style>{css}</style>
    </head>
    <body>
        <h1>Security Hub Findings Summary</h1>
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

        <h2>Compliance Status</h2>
        <table>
            <thead>
                <tr>
                    <th>Status</th>
                    <th>Count</th>
                    <th>Percentage</th>
                </tr>
            </thead>
            <tbody>"""

    for status, count in aggregated_data_report["ComplianceStatus"].items():
        percentage = (count / total_findings) * 100
        html += f"""
                <tr>
                    <td>{status}</td>
                    <td>{count}</td>
                    <td>{percentage:.1f}%</td>
                </tr>"""

    html += """
            </tbody>
        </table>

        <h2>Top 5 Resource Types Affected</h2>
        <ul>"""

    sorted_resource_types = sorted(
        aggregated_data_report["ResourceType"].items(),
        key=lambda item: item[1],
        reverse=True,
    )
    for resource_type, count in sorted_resource_types[:5]:
        html += f"<li>{resource_type}: {count}</li>"

    html += """
        </ul>

        <h2>Findings by Service</h2>
        <ul>"""

    for service, count in aggregated_data_report["Service"].items():
        html += f"<li>{service}: {count}</li>"

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Retrieve and aggregate Security Hub findings."
    )
    parser.add_argument("--profile", required=True, help="AWS profile name")
    parser.add_argument(
        "--region", default="us-west-2", help="AWS region (default: us-west-2)"
    )
    args = parser.parse_args()

    security_findings = get_security_findings(args.profile, args.region)

    if security_findings:
        aggregate_data = process_findings(security_findings)
        aggregate_findings = len(security_findings)

        # Generate HTML content
        html_report = generate_pdf_report(aggregate_data, aggregate_findings)

        # Generate filename with timestamp
        right_now = datetime.now()
        date_time_stamp = right_now.strftime("%Y%m%d_%H%M%S")  # Format for filename
        filename = f"security_hub_report_{date_time_stamp}.pdf"

        # Convert HTML to PDF using pdfkit
        pdfkit.from_string(html_report, filename)

        print(f"\nReport generated: {filename}")
