#!/usr/bin/env python3

""""
Query an S3 bucket for VPC flow logs that contain a specific port number and IP address.

"""

import argparse
import gzip
from datetime import datetime, timedelta
import boto3

def search_logs_in_s3(
    bucket_name,
    folder_path,
    aws_profile,
    port_number,
    ip_address,
    time_range_hours
):
    """
    Search log files in an S3 bucket for a specific port number and IP address within a time range.
    """
    session = boto3.Session(profile_name=aws_profile)
    s3_client = session.client('s3')

    # Calculate the time range
    now = datetime.now()
    time_range_start = now - timedelta(hours=time_range_hours)

    # List objects in the specified folder
    objects = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_path)

    if 'Contents' in objects:
        for obj in objects['Contents']:
            key = obj['Key']
            response = s3_client.get_object(Bucket=bucket_name, Key=key)

            # Check the last modified time of the log file
            last_modified = obj['LastModified'].replace(tzinfo=None)

            # Only process log files within the specified time range
            if time_range_start <= last_modified <= now:
                # Extract log content from the object
                log_content = response['Body'].read()

                # Check if the log file is gzip-compressed
                if response.get('ContentEncoding') == 'gzip':
                    log_content = gzip.decompress(log_content).decode('utf-8')

                # Convert log_content to a string
                log_content = str(log_content)

                # Search for desired patterns in log content
                if f'dstPort={port_number}' in log_content and f'srcIP={ip_address}' in log_content:
                    print(f"Log file: s3://{bucket_name}/{key}")
                    print(log_content)
                    print("-" * 80)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Search log files in an S3 bucket')
    parser.add_argument('--bucket', required=True, type=str, help='Name of the S3 bucket')
    parser.add_argument('--folder', required=True, type=str, help='Folder path within the bucket')
    parser.add_argument('--profile', required=True, type=str, help='AWS profile name')
    parser.add_argument('--port', required=True, type=int, help='Port number to search')
    parser.add_argument('--ip', required=True, help='IP address to search')
    parser.add_argument('--time-range', default=3, type=int,
                        help='Time range in hours (default: 3)')
    args = parser.parse_args()

    search_logs_in_s3(args.bucket, args.folder, args.profile, args.port, args.ip, args.time_range)
