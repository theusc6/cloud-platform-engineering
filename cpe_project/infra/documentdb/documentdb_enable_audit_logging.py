"""
This module provides a script to enable audit logging for Amazon DocumentDB clusters.
The script can be tailored to target a single cluster or multiple clusters within a 
specified AWS region. It utilizes the AWS SDK for Python (boto3) to interact with 
the AWS services and requires AWS credentials, which can be provided through an AWS 
SO profile. The main function orchestrates the process, parsing the command-line
arguments to determine the target cluster(s) and initiating the logging enablement process.
"""
import argparse
import boto3
from botocore.exceptions import ClientError

def parse_args():
    """
    Parse command-line arguments passed to the script.
    """
    parser = argparse.ArgumentParser(
        description='Enable audit logging for Amazon DocumentDB clusters.'
    )
    parser.add_argument('--profile', '-p', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('--region', '-r', required=True, type=str,
                        help='AWS region for the DocumentDB cluster')
    parser.add_argument('--cluster-identifier', '-c', required=False, type=str, default=None,
                        help='The identifier for the DocumentDB cluster (optional)')
    return parser.parse_args()

def enable_documentdb_audit_logging(docdb_client, cluster_identifier):
    """
    Enable audit logging for a specific Amazon DocumentDB cluster.
    """
    print(f'Enabling audit logging for cluster: {cluster_identifier}')

    # Modify the DocumentDB cluster to enable audit logging
    try:
        docdb_client.modify_db_cluster(
            DBClusterIdentifier=cluster_identifier,
            CloudwatchLogsExportConfiguration={
                'EnableLogTypes': ['audit']
            },
            ApplyImmediately=True
        )
        print(f'Audit logging enabled for cluster: {cluster_identifier}')
    except ClientError as client_error:
        print(f'Error enabling audit logging for cluster: {cluster_identifier},'
              f'Error: {client_error}')

def process_documentdb_clusters(docdb_client, cluster_identifier=None):
    """
    Process DocumentDB clusters and enable audit logging.
    If a cluster_identifier is provided, enable logging for that cluster only.
    """
    if cluster_identifier:
        enable_documentdb_audit_logging(docdb_client, cluster_identifier)
    else:
        # Get the list of DocumentDB clusters
        clusters = docdb_client.describe_db_clusters()['DBClusters']
        # Process each cluster
        for cluster in clusters:
            cluster_identifier = cluster['DBClusterIdentifier']
            enable_documentdb_audit_logging(docdb_client, cluster_identifier)

def main():
    """
    The main function of the script.
    It parses command-line arguments, initializes a session with AWS,
    and enables audit logging for the specified DocumentDB clusters.
    If a specific cluster identifier is provided, it enables audit logging
    for that cluster only; otherwise, it enables logging for all clusters.
    """
    args = parse_args()

    # Initialize a session using AWS SSO
    session = boto3.Session(profile_name=args.profile, region_name=args.region)

    # Create the DocumentDB client
    docdb_client = session.client('docdb')

    # Process and enable audit logging for the specified DocumentDB cluster(s)
    process_documentdb_clusters(docdb_client, args.cluster_identifier)

if __name__ == "__main__":
    main()
