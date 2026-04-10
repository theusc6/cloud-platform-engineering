"""
CloudWatch Dashboard Generator and Deployer
"""

import argparse
import json
import boto3
import botocore.exceptions
import yaml

def generate_dashboard_template(resources, dashboard_name):
    """
    Generate CloudFormation template for CloudWatch dashboard
    """
    widgets = generate_widgets(resources)

    dashboard_body = {
        "widgets": widgets
    }

    template = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Resources": {
            "CloudWatchDashboard": {
                "Type": "AWS::CloudWatch::Dashboard",
                "Properties": {
                    "DashboardName": dashboard_name,
                    "DashboardBody": json.dumps(dashboard_body)
                }
            }
        }
    }

    return template

def generate_widgets(resources):
    """
    Generate CloudWatch dashboard widgets
    """
    widgets = []
    for service, resource_count in resources.items():
        widgets.append({
            "type": "metric",
            "x": 0,
            "y": resource_count * 6,
            "width": 12,
            "height": 6,
            "properties": {
                "metrics": [
                    [f"AWS/{service}", "Count", "Resource", f"My{service}Name"]
                ],
                "view": "timeSeries",
                "stacked": False,
                "title": f"{service} Metrics",
                "region": "us-west-2"
            }
        })
    return widgets

def main():
    """
    Main function for generating CloudFormation template and creating CloudWatch dashboard.
    """
    parser = argparse.ArgumentParser(description="Generate CloudFormation template")
    parser.add_argument("-p", "--profile", required=True, help="AWS profile name")
    parser.add_argument("-d", "--dashboard-name", required=True, help="Dashboard name")
    args = parser.parse_args()

    session = boto3.Session(profile_name=args.profile)
    cloudwatch_client = session.client("cloudwatch")

    paginator = cloudwatch_client.get_paginator("list_metrics")
    resources = {}
    for response in paginator.paginate():
        for metric in response["Metrics"]:
            service = metric["Namespace"].split("/")[1]
            resources[service] = resources.get(service, 0) + 1

    print("Metrics that will be created into Dashboard widgets:")
    for service in resources:
        print(f"- {service} Metrics")

    user_input = input("Do you want to continue? (Y/n): ").lower()
    if user_input not in ("y", ""):
        print("Script execution terminated.")
        return

    dashboard_template = generate_dashboard_template(resources, args.dashboard_name)

    with open(f"{args.dashboard_name}_template.yaml", "w", encoding="utf-8") as yaml_file:
        yaml.dump(dashboard_template, yaml_file, default_flow_style=False)

    try:
        cloudformation_client = session.client("cloudformation")
        response = cloudformation_client.create_stack(
            StackName=args.dashboard_name,
            TemplateBody=json.dumps(dashboard_template),
            Capabilities=["CAPABILITY_IAM"],
        )
        print("Stack creation initiated. Stack ID:", response["StackId"])
    except botocore.exceptions.ClientError as error:
        error_code = error.response["Error"]["Code"]
        if error_code == "AlreadyExistsException":
            print("A stack with the same name already exists. Choose a different name.")
        else:
            print("An error occurred while creating the stack:", str(error))
    except botocore.exceptions.BotoCoreError as error:
        print("An AWS-specific error occurred:", str(error))

if __name__ == "__main__":
    main()
