#!/usr/bin/env python3

"""
This module tests an EventBridge connection from
within MyOrg to an externally defined AWS ARN.

Tests cross-account EventBridge event delivery.
"""

import json
import argparse
from botocore.exceptions import ClientError
import boto3

EVENT_BUS_NAME = (
    'arn:aws:events:eu-west-2:123456789012:'
    'event-bus/redacted-service-redacted-labs-integration-myorg'
)
EVENT_BUS_REGION = 'eu-west-2'

def parse_args():
    """
    Parse command-line arguments passed to the script.
    """
    parser = argparse.ArgumentParser(
        description='Emit events for a specific event bus.'
        )
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    return parser.parse_args()

def emit(client, type, event):
    """
    Emit an event to the specified event bus.
    """
    try:

        response = client.put_events(
            Entries=[
                {
                    'Source': 'myorg.event-streams',
                    'DetailType': type,
                    'Detail': json.dumps(event),
                    'EventBusName': EVENT_BUS_NAME
                },
            ]
        )
        print(f"Event emitted successfully, Response: {response}")
    except ClientError as client_error:
        error_message = client_error.response.get(
            'Error', {}
        ).get(
            'Message', 'Unknown error occurred'
        )
        print(f"An error occurred while emitting event: {error_message}")

def main():
    """
    Main function of the script.
    """
    args = parse_args()
    session = boto3.Session(profile_name=args.profile)
    client = session.client('events', region_name=EVENT_BUS_REGION)

    event = {
        "id": "111",
        "when": "2023-07-12T15:00:00Z",
        "correlation_id": "111",
        "payload": {
            "report_number": "111",
            "redacted_id": "111"
        }
    }

    emit(client, 'report:created', event)

if __name__ == "__main__":
    main()
