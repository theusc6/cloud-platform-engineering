"""
This script deletes Amazon Web Services (AWS) Elastic Block Store 
(EBS) snapshots based on a specific tag key and value.
It utilizes AWS Boto3 SDK for Python to interact with the AWS EC2 service, 
specifically to list and delete EBS snapshots.
"""

from datetime import datetime
import argparse
import boto3
from botocore.exceptions import ClientError

BACKUP_VAULT_NAME = 'Default'

def attempt_delete_snapshot(ec2_client, backup_client, snapshot_id, region):
    '''
    Attempts to delete an EBS snapshot using the EC2 client. If the snapshot is managed
    by AWS Backup and cannot be deleted directly, it attempts deletion via the backup client.
    '''
    try:
        ec2_client.delete_snapshot(SnapshotId=snapshot_id)
        print(f"Successfully deleted snapshot: {snapshot_id}")
        return True
    except ClientError as error:
        return handle_delete_snapshot_error(error, backup_client, snapshot_id, region) or False

def handle_delete_snapshot_error(error, backup_client, snapshot_id, region):
    '''
    Handles errors encountered during the snapshot deletion process. If the snapshot is in use or
    managed by AWS Backup, it takes appropriate actions based on the error type.
    '''
    error_code = error.response['Error']['Code']
    if error_code == 'InvalidSnapshot.InUse':
        print(f"Skipping deletion of {snapshot_id} as it is currently in use.")
        return False
    if "managed by the AWS Backup service" in error.response['Error']['Message']:
        print(f"Snapshot {snapshot_id} is managed by AWS Backup. "
              f"Attempting to delete via AWS Backup APIs...")
        return attempt_delete_backup_snapshot(backup_client, snapshot_id, region)

    print(f"Error deleting snapshot {snapshot_id}: {error.response['Error']['Message']}")
    return False

def attempt_delete_backup_snapshot(backup_client, snapshot_id, region):
    '''
    Attempts to delete a snapshot's associated AWS Backup recovery point. This is typically
    called when a snapshot is managed by AWS Backup and cannot be deleted directly via EC2 APIs.
    '''
    recovery_point_arn = f'arn:aws:ec2:{region}::snapshot/{snapshot_id}'
    try:
        backup_client.delete_recovery_point(BackupVaultName=BACKUP_VAULT_NAME,
                                            RecoveryPointArn=recovery_point_arn)
        print(f"Successfully requested deletion of AWS Backup "
              f"recovery point for snapshot: {snapshot_id}")
        return True
    except ClientError as error:
        print(f"Failed to delete AWS Backup recovery point for snapshot {snapshot_id}: {error}")
        return False

def filter_snapshots_by_criteria(snapshot, tag_key, tag_value, cutoff_date, search_string):
    '''
    Filters snapshots based on the provided criteria including a cutoff date, a specific tag key,
    a tag key-value pair, or no tags at all, and optionally a search string in the description.
    '''
    snapshot_date = snapshot['StartTime'].replace(tzinfo=None)

    # Ensure the snapshot is older than the cutoff date
    if snapshot_date >= cutoff_date:
        return False

    # Check if search_string is provided and matches the description
    if search_string and search_string.lower() in snapshot.get('Description', '').lower():
        return True

    # If no tag_key is provided, match snapshots that have no tags at all
    if not tag_key:
        if 'Tags' not in snapshot or not snapshot['Tags']:
            print(f"Snapshot {snapshot['SnapshotId']} has no tags.")
            return True
        return False

    # If a tag_key is provided but no tag_value, match snapshots that have the specified key, regardless of value
    if tag_key and not tag_value:
        if 'Tags' in snapshot:
            for tag in snapshot['Tags']:
                if tag['Key'] == tag_key:
                    print(f"Snapshot {snapshot['SnapshotId']} has the tag key '{tag_key}' with any value.")
                    return True
        return False

    # If both tag_key and tag_value are provided, match only those with the exact key-value pair
    if tag_key and tag_value and 'Tags' in snapshot:
        for tag in snapshot['Tags']:
            if tag['Key'] == tag_key and tag['Value'] == tag_value:
                print(f"Snapshot {snapshot['SnapshotId']} matches tag '{tag_key}: {tag_value}'.")
                return True

    # If none of the conditions matched, return False
    return False

def delete_snapshots_by_tag_and_date(ec2_client, backup_client, config):
    '''
    Deletes EBS snapshots based on the specified tag key, value, a cutoff date, and optionally
    a search string in the snapshot description. This function utilizes a paginator to list all
    snapshots and filters them based on the provided criteria.
    '''
    deleted_count = 0
    paginator = ec2_client.get_paginator('describe_snapshots')
    page_iterator = paginator.paginate(OwnerIds=['self'])

    for page in page_iterator:
        for snapshot in page['Snapshots']:
            if filter_snapshots_by_criteria(snapshot, config['tag_key'], config['tag_value'],
                                            config['cutoff_date'], config.get('search_string', '')):
                snapshot_id = snapshot['SnapshotId']
                print(f"Attempting to delete snapshot {snapshot_id}...")
                if attempt_delete_snapshot(ec2_client, backup_client,
                                           snapshot_id, config['region']):
                    deleted_count += 1

    print(f"Total snapshots deleted: {deleted_count}")

def main():
    '''
    Parses command-line arguments, establishes an AWS session,
    and deletes snapshots based on the specified tag key and value.
    '''
    parser = argparse.ArgumentParser(description="Delete AWS EBS Snapshots Based on Tag")
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('-t', '--tag', required=False, type=str,
                        help='Tag key to filter snapshots for deletion')
    parser.add_argument('-v', '--value', required=False, type=str,
                        help='Tag value to filter snapshots for deletion')
    parser.add_argument('-r', '--region', required=False, default="us-west-2",
                        type=str, help='AWS region to operate in')
    parser.add_argument('-d', '--date', required=True, type=str,
                        help='Cutoff date for deleting snapshots. Format: YYYY-MM-DD')
    parser.add_argument('-s', '--search-string', required=False, default="",
                        type=str, help='String to search for in snapshot descriptions')

    args = parser.parse_args()
    cutoff_date = datetime.strptime(args.date, "%Y-%m-%d")
    config = {
        'tag_key': args.tag,
        'tag_value': args.value,
        'cutoff_date': cutoff_date,
        'region': args.region,
        'search_string': args.search_string 
    }

    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    ec2_client = session.client('ec2')
    backup_client = session.client('backup')

    delete_snapshots_by_tag_and_date(ec2_client, backup_client, config)

if __name__ == "__main__":
    main()
