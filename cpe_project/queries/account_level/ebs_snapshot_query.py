"""
This module provides functionality to fetch details of AWS EBS snapshots 
associated with a specific AWS account and export those details into an
Excel file. It utilizes the AWS SDK for Python (Boto3) to interact with AWS services and
Pandas to manage and export the snapshot data.

The script allows for command-line input to specify the AWS CLI profile and AWS region
to use for fetching snapshot details. It captures information such as Snapshot ID, Volume 
ID, Snapshot State, Start Time, Volume Size, Name tag (if available), Description, Snapshot 
Type, and Volume Type. This data is then exported to an Excel file named 'ebs_snapshots.xlsx'.
"""

from datetime import datetime
import argparse
import boto3
import pandas as pd


def get_ebs_snapshots(ec2_client):
    """
    Fetches all EBS snapshots for the AWS account associated with the given EC2 client and includes
    the "Name" tag value, snapshot type, volume type, description, etc.
    """
    snapshots = ec2_client.describe_snapshots(OwnerIds=['self'])['Snapshots']
    snapshots_list = []

    for snapshot in snapshots:
        snapshot_name = None  # Default name
        volume_type = 'N/A'  # Default volume type

        # Extract snapshot tags and description
        snapshot_description = snapshot.get('Description', 'N/A')
        storage_tier = snapshot.get('StorageTier', 'N/A')

        # Check if 'Tags' exist and find the 'Name' tag
        if 'Tags' in snapshot:
            snapshot_name = next((tag['Value']
                                  for tag in snapshot['Tags'] if tag['Key'] == 'Name'), None)

        volume_id = snapshot['VolumeId']
        try:
            volume_info = ec2_client.describe_volumes(VolumeIds=[volume_id])['Volumes'][0]
            volume_type = volume_info['VolumeType']
        except ec2_client.exceptions.ClientError as client_error:
            if client_error.response['Error']['Code'] == 'InvalidVolume.NotFound':
                print(f"Volume {volume_id} for snapshot {snapshot['SnapshotId']} not found.")
            else:
                raise  # If the exception is not 'InvalidVolume.NotFound', let it raise.

        snapshots_list.append({
            'SnapshotId': snapshot['SnapshotId'],
            'VolumeId': volume_id,
            'State': snapshot['State'],
            'StartTime': snapshot['StartTime'].strftime('%Y-%m-%d %H:%M:%S'),
            'VolumeSize': snapshot['VolumeSize'],
            'Name': snapshot_name,
            'Description': snapshot_description,
            'StorageTier': storage_tier,
            'VolumeType': volume_type,
            'Owner': snapshot['OwnerId'],
            'Encrypted': snapshot['Encrypted']
        })

        print(f"Gathering information for snapshot {snapshot['SnapshotId']}..")

    return snapshots_list

def export_snapshots_to_excel(snapshots_list, file_name):
    """
    Exports EBS snapshot details to an Excel file.

    :param snapshots_list: A list of dictionaries with EBS snapshot details.
    :param file_name: Name of the Excel file to create.
    """
    data_frame = pd.DataFrame(snapshots_list)
    data_frame.to_excel(file_name, index=False)
    print(f'Successfully created {file_name} with details of EBS snapshots.')

def main():
    """
    Main function to process command-line arguments and initiate snapshot fetching and exporting.
    """
    # Initialize the argument parser
    parser = argparse.ArgumentParser(description='List EBS snapshots to an Excel file.')
    parser.add_argument('-p', '--profile', type=str, required=True, help='AWS CLI profile name')
    parser.add_argument('-r','--region', type=str, required=False, default="us-west-2",
                        help='AWS region')

    # Parse arguments
    args = parser.parse_args()

    # Configure Boto3 to use the specified profile and region
    boto3.setup_default_session(profile_name=args.profile, region_name=args.region)
    ec2_client = boto3.client('ec2')

    # get the account_id from the current session
    account_id = boto3.client('sts').get_caller_identity().get('Account')

    date_time = datetime.now().date()
    file_name = f'ebs_snapshots_{account_id}_{date_time}.xlsx'

    # Fetch EBS snapshots and export them to an Excel file
    snapshots_list = get_ebs_snapshots(ec2_client)
    export_snapshots_to_excel(snapshots_list, file_name)

if __name__ == "__main__":
    main()
