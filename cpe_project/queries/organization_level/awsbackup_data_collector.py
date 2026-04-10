"""
This module queries AWS resources (not snapshots) to estimate future backup costs.
It collects actual resource sizes that would be backed up by AWS Backup.
"""
import argparse
from datetime import datetime, timedelta
import boto3
import pandas as pd
from botocore.exceptions import BotoCoreError, ClientError


def find_dynamodb_tables(aws_region, session, account_id, account_name):
    """Retrieves DynamoDB tables (actual resources, not snapshots)."""
    try:
        dynamodb_client = session.client('dynamodb', region_name=aws_region)
        paginator = dynamodb_client.get_paginator('list_tables')
        table_names = []

        for page in paginator.paginate():
            table_names.extend(page.get('TableNames', []))

        data = []
        for table_name in table_names:
            try:
                response = dynamodb_client.describe_table(TableName=table_name)
                table = response['Table']
                table_size_bytes = table.get('TableSizeBytes', 0)
                table_size_gb = table_size_bytes / (1024 ** 3)

                table_data = {
                    'Table Name': table_name,
                    'Status': table.get('TableStatus', 'UNKNOWN'),
                    'Size (Bytes)': table_size_bytes,
                    'Size (GB)': round(table_size_gb, 4),
                    'Item Count': table.get('ItemCount', 0),
                    'Billing Mode': table.get('BillingModeSummary', 
                                              {}).get('BillingMode', 'PROVISIONED'),
                    'Region': aws_region,
                    'Account ID': account_id,
                    'Account Name': account_name
                }
                data.append(table_data)
                print(f'Found DynamoDB Table - {table_name}: {round(table_size_gb, 4)} GB')
            except ClientError as e:
                print(f"Error: {str(e)}")
        return data
    except ClientError as e:
        print(f"Error accessing DynamoDB in {aws_region}: {str(e)}")
        return []


def find_efs_filesystems(aws_region, session, account_id, account_name):
    """Retrieves EFS file systems (actual resources, not snapshots)."""
    try:
        efs_client = session.client('efs', region_name=aws_region)
        paginator = efs_client.get_paginator('describe_file_systems')

        data = []
        for page in paginator.paginate():
            for fs in page.get('FileSystems', []):
                fs_size_bytes = fs.get('SizeInBytes', {}).get('Value', 0)
                fs_size_gb = fs_size_bytes / (1024 ** 3)

                fs_data = {
                    'File System ID': fs['FileSystemId'],
                    'Name': fs.get('Name', 'N/A'),
                    'Lifecycle State': fs.get('LifeCycleState', 'UNKNOWN'),
                    'Size (Bytes)': fs_size_bytes,
                    'Size (GB)': round(fs_size_gb, 4),
                    'Performance Mode': fs.get('PerformanceMode', 'N/A'),
                    'Encrypted': fs.get('Encrypted', False),
                    'Region': aws_region,
                    'Account ID': account_id,
                    'Account Name': account_name
                }
                data.append(fs_data)
                print(f'Found EFS - {fs["FileSystemId"]}: {round(fs_size_gb, 4)} GB')
        return data
    except ClientError as e:
        print(f"Error accessing EFS in {aws_region}: {str(e)}")
        return []


def find_ebs_volumes(aws_region, session, account_id, account_name):
    """Retrieves EBS volumes (actual volumes, not snapshots)."""
    try:
        ec2_client = session.client('ec2', region_name=aws_region)
        paginator = ec2_client.get_paginator('describe_volumes')

        data = []
        for page in paginator.paginate():
            for volume in page.get('Volumes', []):
                volume_name = 'N/A'
                if volume.get('Tags'):
                    for tag in volume['Tags']:
                        if tag['Key'] == 'Name':
                            volume_name = tag['Value']
                            break

                volume_data = {
                    'Volume ID': volume.get('VolumeId', 'N/A'),
                    'Name': volume_name,
                    'Size (GB)': volume.get('Size', 0),
                    'Volume Type': volume.get('VolumeType', 'N/A'),
                    'State': volume.get('State', 'UNKNOWN'),
                    'Encrypted': volume.get('Encrypted', False),
                    'Attached Instance': volume['Attachments'][0]['InstanceId'] if volume.get('Attachments') else 'Not Attached',
                    'Region': aws_region,
                    'Account ID': account_id,
                    'Account Name': account_name
                }
                data.append(volume_data)
                print(f'Found EBS Volume - {volume["VolumeId"]}: {volume_data["Size (GB)"]} GB')
        return data
    except ClientError as e:
        print(f"Error accessing EBS in {aws_region}: {str(e)}")
        return []


def find_rds_instances(aws_region, session, account_id, account_name):
    """Retrieves RDS instances (actual databases, not snapshots)."""
    try:
        rds_client = session.client('rds', region_name=aws_region)
        paginator = rds_client.get_paginator('describe_db_instances')

        data = []
        for page in paginator.paginate():
            for instance in page.get('DBInstances', []):
                instance_data = {
                    'DB Instance ID': instance.get('DBInstanceIdentifier', 'N/A'),
                    'DB Name': instance.get('DBName', 'N/A'),
                    'Size (GB)': instance.get('AllocatedStorage', 0),
                    'Status': instance.get('DBInstanceStatus', 'UNKNOWN'),
                    'Engine': instance.get('Engine', 'N/A'),
                    'Engine Version': instance.get('EngineVersion', 'N/A'),
                    'Instance Class': instance.get('DBInstanceClass', 'N/A'),
                    'Multi-AZ': instance.get('MultiAZ', False),
                    'Encrypted': instance.get('StorageEncrypted', False),
                    'Region': aws_region,
                    'Account ID': account_id,
                    'Account Name': account_name
                }
                data.append(instance_data)
                print(f'Found RDS Instance - {instance_data["DB Instance ID"]}: {instance_data["Size (GB)"]} GB')
        return data
    except ClientError as e:
        print(f"Error accessing RDS in {aws_region}: {str(e)}")
        return []


def find_aurora_clusters(aws_region, session, account_id, account_name):
    """Retrieves Aurora clusters (actual clusters, not snapshots)."""
    try:
        rds_client = session.client('rds', region_name=aws_region)
        paginator = rds_client.get_paginator('describe_db_clusters')

        data = []
        for page in paginator.paginate():
            for cluster in page.get('DBClusters', []):
                cluster_data = {
                    'Cluster ID': cluster.get('DBClusterIdentifier', 'N/A'),
                    'Size (GB)': cluster.get('AllocatedStorage', 0),
                    'Status': cluster.get('Status', 'UNKNOWN'),
                    'Engine': cluster.get('Engine', 'N/A'),
                    'Engine Version': cluster.get('EngineVersion', 'N/A'),
                    'Multi-AZ': cluster.get('MultiAZ', False),
                    'Encrypted': cluster.get('StorageEncrypted', False),
                    'Region': aws_region,
                    'Account ID': account_id,
                    'Account Name': account_name
                }
                data.append(cluster_data)
                print(f'Found Aurora Cluster - {cluster_data["Cluster ID"]}: {cluster_data["Size (GB)"]} GB')
        return data
    except ClientError as e:
        print(f"Error accessing Aurora in {aws_region}: {str(e)}")
        return []


def find_fsx_windows_filesystems(aws_region, session, account_id, account_name):
    """Retrieves FSx for Windows file systems (actual file systems, not backups)."""
    try:
        fsx_client = session.client('fsx', region_name=aws_region)
        paginator = fsx_client.get_paginator('describe_file_systems')

        data = []
        for page in paginator.paginate():
            for fs in page.get('FileSystems', []):
                if fs.get('FileSystemType') == 'WINDOWS':
                    fs_data = {
                        'File System ID': fs.get('FileSystemId', 'N/A'),
                        'Size (GB)': fs.get('StorageCapacity', 0),
                        'Lifecycle': fs.get('Lifecycle', 'UNKNOWN'),
                        'Storage Type': fs.get('StorageType', 'N/A'),
                        'Region': aws_region,
                        'Account ID': account_id,
                        'Account Name': account_name
                    }
                    data.append(fs_data)
                    print(f'Found FSx Windows - {fs_data["File System ID"]}: {fs_data["Size (GB)"]} GB')
        return data
    except ClientError as e:
        print(f"Error accessing FSx Windows in {aws_region}: {str(e)}")
        return []


def find_fsx_lustre_filesystems(aws_region, session, account_id, account_name):
    """Retrieves FSx for Lustre file systems (actual file systems, not backups)."""
    try:
        fsx_client = session.client('fsx', region_name=aws_region)
        paginator = fsx_client.get_paginator('describe_file_systems')

        data = []
        for page in paginator.paginate():
            for fs in page.get('FileSystems', []):
                if fs.get('FileSystemType') == 'LUSTRE':
                    fs_data = {
                        'File System ID': fs.get('FileSystemId', 'N/A'),
                        'Size (GB)': fs.get('StorageCapacity', 0),
                        'Lifecycle': fs.get('Lifecycle', 'UNKNOWN'),
                        'Storage Type': fs.get('StorageType', 'N/A'),
                        'Region': aws_region,
                        'Account ID': account_id,
                        'Account Name': account_name
                    }
                    data.append(fs_data)
                    print(f'Found FSx Lustre - {fs_data["File System ID"]}: {fs_data["Size (GB)"]} GB')
        return data
    except ClientError as e:
        print(f"Error accessing FSx Lustre in {aws_region}: {str(e)}")
        return []


def find_documentdb_clusters(aws_region, session, account_id, account_name):
    """Retrieves DocumentDB clusters (actual clusters, not snapshots)."""
    try:
        docdb_client = session.client('docdb', region_name=aws_region)
        paginator = docdb_client.get_paginator('describe_db_clusters')

        data = []
        for page in paginator.paginate():
            for cluster in page.get('DBClusters', []):
                cluster_data = {
                    'Cluster ID': cluster.get('DBClusterIdentifier', 'N/A'),
                    'Size (GB)': cluster.get('AllocatedStorage', 0),
                    'Status': cluster.get('Status', 'UNKNOWN'),
                    'Engine': cluster.get('Engine', 'N/A'),
                    'Encrypted': cluster.get('StorageEncrypted', False),
                    'Region': aws_region,
                    'Account ID': account_id,
                    'Account Name': account_name
                }
                data.append(cluster_data)
                print(f'Found DocumentDB - {cluster_data["Cluster ID"]}: {cluster_data["Size (GB)"]} GB')
        return data
    except ClientError as e:
        print(f"Error accessing DocumentDB in {aws_region}: {str(e)}")
        return []


def find_neptune_clusters(aws_region, session, account_id, account_name):
    """Retrieves Neptune clusters (actual clusters, not snapshots)."""
    try:
        neptune_client = session.client('neptune', region_name=aws_region)
        paginator = neptune_client.get_paginator('describe_db_clusters')

        data = []
        for page in paginator.paginate():
            for cluster in page.get('DBClusters', []):
                cluster_data = {
                    'Cluster ID': cluster.get('DBClusterIdentifier', 'N/A'),
                    'Size (GB)': cluster.get('AllocatedStorage', 0),
                    'Status': cluster.get('Status', 'UNKNOWN'),
                    'Engine': cluster.get('Engine', 'N/A'),
                    'Encrypted': cluster.get('StorageEncrypted', False),
                    'Region': aws_region,
                    'Account ID': account_id,
                    'Account Name': account_name
                }
                data.append(cluster_data)
                print(f'Found Neptune - {cluster_data["Cluster ID"]}: {cluster_data["Size (GB)"]} GB')
        return data
    except ClientError as e:
        print(f"Error accessing Neptune in {aws_region}: {str(e)}")
        return []


def find_storage_gateway_volumes(aws_region, session, account_id, account_name):
    """Retrieves Storage Gateway volumes (actual volumes)."""
    try:
        sg_client = session.client('storagegateway', region_name=aws_region)
        gateways = sg_client.list_gateways()

        data = []
        for gateway in gateways.get('Gateways', []):
            gateway_arn = gateway.get('GatewayARN')
            try:
                volumes = sg_client.list_volumes(GatewayARN=gateway_arn)
                for volume_info in volumes.get('VolumeInfos', []):
                    volume_size_gb = volume_info.get('VolumeSizeInBytes', 0) / (1024 ** 3)
                    volume_data = {
                        'Volume ARN': volume_info.get('VolumeARN'),
                        'Volume Type': volume_info.get('VolumeType', 'N/A'),
                        'Size (GB)': round(volume_size_gb, 4),
                        'Gateway ARN': gateway_arn,
                        'Region': aws_region,
                        'Account ID': account_id,
                        'Account Name': account_name
                    }
                    data.append(volume_data)
                    print(f'Found Storage Gateway Volume: {round(volume_size_gb, 4)} GB')
            except ClientError:
                pass
        return data
    except ClientError as e:
        print(f"Error accessing Storage Gateway in {aws_region}: {str(e)}")
        return []


def find_s3_bucket_sizes(session, account_id, account_name):
    """Retrieves S3 bucket sizes."""
    try:
        s3_client = session.client('s3', region_name='us-east-1')
        buckets = s3_client.list_buckets()

        data = []
        for bucket in buckets.get('Buckets', []):
            bucket_name = bucket['Name']
            try:
                location_response = s3_client.get_bucket_location(Bucket=bucket_name)
                bucket_region = location_response.get('LocationConstraint') or 'us-east-1'
                cloudwatch_client = session.client('cloudwatch', region_name=bucket_region)

                end_time = datetime.utcnow()
                start_time = end_time - timedelta(days=1)

                metrics = cloudwatch_client.get_metric_statistics(
                    Namespace='AWS/S3',
                    MetricName='BucketSizeBytes',
                    Dimensions=[
                        {'Name': 'BucketName', 'Value': bucket_name},
                        {'Name': 'StorageType', 'Value': 'StandardStorage'}
                    ],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=86400,
                    Statistics=['Average']
                )

                bucket_size_bytes = 0
                if metrics.get('Datapoints'):
                    bucket_size_bytes = int(metrics['Datapoints'][0].get('Average', 0))

                bucket_size_gb = bucket_size_bytes / (1024 ** 3)

                bucket_data = {
                    'Bucket Name': bucket_name,
                    'Size (Bytes)': bucket_size_bytes,
                    'Size (GB)': round(bucket_size_gb, 4),
                    'Region': bucket_region,
                    'Account ID': account_id,
                    'Account Name': account_name
                }
                data.append(bucket_data)
                print(f'Found S3 Bucket - {bucket_name}: {round(bucket_size_gb, 4)} GB')
            except ClientError as e:
                print(f"Error: {str(e)}")
        return data
    except ClientError as e:
        print(f"Error accessing S3: {str(e)}")
        return []


def get_organization_accounts(master_sess):
    """Fetches a list of accounts in the organization."""
    organizations = master_sess.client('organizations')
    paginator = organizations.get_paginator('list_accounts')
    accounts_list = []

    for page in paginator.paginate():
        accounts_list.extend(page['Accounts'])

    for account in accounts_list:
        print(f'Account ID: {account["Id"]}, Name: {account["Name"]}')

    return accounts_list


def assume_role_in_account(account_id, role_name, session):
    """Assumes a role in the given account."""
    try:
        print(f'\nAssuming role in account {account_id}: arn:aws:iam::{account_id}:role/{role_name}')
        sts = session.client('sts')
        response = sts.assume_role(
            RoleArn=f'arn:aws:iam::{account_id}:role/{role_name}',
            RoleSessionName='AWSBackupCostEstimation'
        )

        return boto3.Session(
            aws_access_key_id=response['Credentials']['AccessKeyId'],
            aws_secret_access_key=response['Credentials']['SecretAccessKey'],
            aws_session_token=response['Credentials']['SessionToken']
        )
    except ClientError as e:
        print(f"Failed to assume role in account {account_id}. Error: {str(e)}")
        return None


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Estimate AWS Backup costs by querying resources.")
    parser.add_argument("--master_account_id", "-id", default="123456789012")
    parser.add_argument("--master_account_name", "-n", default="myorg-master")
    parser.add_argument("--profile_name", "-p", required=True, help="AWS profile name.")
    parser.add_argument("--environment", "-e", choices=['prod', 'dev', 'uat', 'org'], default='org')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    master_session = boto3.Session(profile_name=args.profile_name)

    regions = ["us-east-1", "us-west-2", "us-east-2", "eu-west-2", "ap-southeast-1", "ap-east-1"]

    # Production accounts
    PROD_ACCOUNTS = [
        "123456789012",  # myorg-4cs-prod
        "123456789012",  # myorg-apis-prod
        "123456789012",  # myorg-css-prod
        "123456789012",  # myorg-dig-prod
        "123456789012",  # myorg-facetware-prod
        "123456789012",  # myorg-global-everest-prod
        "123456789012",  # myorg-global-ge-applications-prod
        "123456789012",  # myorg-global-grading-engine-prod
        "123456789012",  # myorg-hk-infra-prod
        "123456789012",  # myorg-app-prod
        "123456789012",  # myorg-labdocs-prod
        "123456789012",  # myorg-labspark-prod
        "123456789012",  # myorg-mpp-prod
        "123456789012",  # myorg-nms-prod
        "123456789012",  # myorg-omd-prod
        "123456789012",  # myorg-sample-app-1-prod
        "123456789012",  # myorg-rds-prod
        "123456789012",  # myorg-sample-app-2-prod
        "123456789012",  # myorg-static-websites-prod
        "123456789012",  # myorg-warp-prod
        "123456789012",  # myorg-wireframe-matching-prod
        "123456789012",  # Log Archive
        "123456789012",  # Security Tooling
        "123456789012",  # myorg-iam
        "123456789012",  # myorg-master
        "123456789012",  # Audit
        "123456789012",  # devops
        "123456789012",  # MyOrg WebServers
        "123456789012",  # MyOrg-ReportResults-DataLake
        "123456789012",  # myorg-security
        "123456789012",  # myorg-shared-services
        "123456789012",  # myorg-ai-training
        "123456789012",  # MyOrg-DataSci
        "123456789012",  # myorg-drives
        "123456789012",  # MyOrg-Network
    ]

    # Development accounts
    DEV_ACCOUNTS = [
        "123456789012",  # myorg-4cs-dev
        "123456789012",  # myorg-agd-dev
        "123456789012",  # myorg-apis-dev
        "123456789012",  # myorg-css-dev
        "123456789012",  # myorg-dig-dev
        "123456789012",  # myorg-everest-dev
        "123456789012",  # myorg-facetware-dev
        "123456789012",  # myorg-global-ge-applications-dev
        "123456789012",  # myorg-grading-engine-dev
        "123456789012",  # myorg-iam-dev
        "123456789012",  # myorg-app-dev
        "123456789012",  # myorg-labdocs-dev
        "123456789012",  # myorg-labspark-dev
        "123456789012",  # myorg-mpp-dev
        "123456789012",  # myorg-nms-dev
        "123456789012",  # myorg-sample-app-1-dev
        "123456789012",  # myorg-rds-dev
        "123456789012",  # myorg-sample-app-2-dev
        "123456789012",  # myorg-static-websites-dev
        "123456789012",  # myorg-verifier-dev
        "123456789012",  # myorg-warp-dev
        "123456789012",  # myorg-wireframe-matching-dev
        "123456789012",  # myorg-training
    ]

    # UAT accounts
    UAT_ACCOUNTS = [
        "123456789012",  # myorg-4cs-uat
        "123456789012",  # myorg-dig-uat
        "123456789012",  # myorg-facetware-uat
        "123456789012",  # myorg-iam-uat
        "123456789012",  # myorg-app-uat
        "123456789012",  # myorg-mpp-uat
        "123456789012",  # myorg-nms-uat
        "123456789012",  # myorg-sample-app-1-uat
        "123456789012",  # myorg-sample-app-2-uat
        "123456789012",  # myorg-warp-uat
        "123456789012",  # myorg-rds-test
        "123456789012",  # myorg-aws-grading-engine-shared
        "123456789012",  # myorg-global-everest-shared
        "123456789012",  # myorg-global-everest-stage
        "123456789012",  # myorg-mpp-shared
    ]

    ENVIRONMENT = args.environment
    accounts = get_organization_accounts(master_session)
    print(f'Found {len(accounts)} accounts in the organization.')

    CROSS_ACCOUNT_ROLE_NAME = 'OrganizationAccountAccessRole'
    MASTER_ACCOUNT_ID = args.master_account_id
    MASTER_ACCOUNT_NAME = args.master_account_name
    master_account = {'Id': MASTER_ACCOUNT_ID, 'Name': MASTER_ACCOUNT_NAME}

    accounts = [account for account in accounts if account['Id'] != MASTER_ACCOUNT_ID]
    accounts.append(master_account)

    if ENVIRONMENT != 'org':
        if ENVIRONMENT == 'prod':
            accounts = [account for account in accounts if account['Id'] in PROD_ACCOUNTS]
            print(f'Filtering for PRODUCTION accounts: {len(accounts)} accounts')
        elif ENVIRONMENT == 'dev':
            accounts = [account for account in accounts if account['Id'] in DEV_ACCOUNTS]
            print(f'Filtering for DEVELOPMENT accounts: {len(accounts)} accounts')
        elif ENVIRONMENT == 'uat':
            accounts = [account for account in accounts if account['Id'] in UAT_ACCOUNTS]
            print(f'Filtering for UAT accounts: {len(accounts)} accounts')

    # Collect resource data
    dynamodb_data, efs_data, ebs_data, rds_data, aurora_data = [], [], [], [], []
    fsx_windows_data, fsx_lustre_data, documentdb_data, neptune_data = [], [], [], []
    storage_gateway_data, s3_data = [], []

    for acct in accounts:
        try:
            account_session = master_session if acct['Id'] == MASTER_ACCOUNT_ID else \
                            assume_role_in_account(acct['Id'], CROSS_ACCOUNT_ROLE_NAME, master_session)

            if account_session is None:
                print(f"Skipping account {acct['Id']}")
                continue

            print(f'\nSearching resources in account {acct["Id"]} ({acct["Name"]}):')
            s3_data.extend(find_s3_bucket_sizes(account_session, acct['Id'], acct['Name']))

            for region in regions:
                try:
                    dynamodb_data.extend(find_dynamodb_tables(region, account_session, acct['Id'], acct['Name']))
                    efs_data.extend(find_efs_filesystems(region, account_session, acct['Id'], acct['Name']))
                    ebs_data.extend(find_ebs_volumes(region, account_session, acct['Id'], acct['Name']))
                    rds_data.extend(find_rds_instances(region, account_session, acct['Id'], acct['Name']))
                    aurora_data.extend(find_aurora_clusters(region, account_session, acct['Id'], acct['Name']))
                    fsx_windows_data.extend(find_fsx_windows_filesystems(region, account_session,
                                                                         acct['Id'], acct['Name']))
                    fsx_lustre_data.extend(find_fsx_lustre_filesystems(region, account_session,
                                                                       acct['Id'], acct['Name']))
                    documentdb_data.extend(find_documentdb_clusters(region, account_session,
                                                                    acct['Id'], acct['Name']))
                    neptune_data.extend(find_neptune_clusters(region, account_session, acct['Id'], acct['Name']))
                    storage_gateway_data.extend(find_storage_gateway_volumes(region, account_session,
                                                                             acct['Id'], acct['Name']))
                except BotoCoreError as e:
                    print(f'Error in region {region}: {str(e)}')
        except BotoCoreError as e:
            print(f'Error in account {acct["Id"]}: {str(e)}')

    # Create DataFrames
    dynamodb_df = pd.DataFrame(dynamodb_data)
    efs_df = pd.DataFrame(efs_data)
    ebs_df = pd.DataFrame(ebs_data)
    rds_df = pd.DataFrame(rds_data)
    aurora_df = pd.DataFrame(aurora_data)
    fsx_windows_df = pd.DataFrame(fsx_windows_data)
    fsx_lustre_df = pd.DataFrame(fsx_lustre_data)
    documentdb_df = pd.DataFrame(documentdb_data)
    neptune_df = pd.DataFrame(neptune_data)
    storage_gateway_df = pd.DataFrame(storage_gateway_data)
    s3_df = pd.DataFrame(s3_data)

    OUTPUT_FILENAME = f'AWS_Backup_Cost_Estimation_{ENVIRONMENT.upper()}.xlsx'

    with pd.ExcelWriter(OUTPUT_FILENAME) as writer:
        if len(dynamodb_df) > 0:
            dynamodb_df.to_excel(writer, sheet_name='DynamoDB Tables', index=False)
        if len(efs_df) > 0:
            efs_df.to_excel(writer, sheet_name='EFS File Systems', index=False)
        if len(ebs_df) > 0:
            ebs_df.to_excel(writer, sheet_name='EBS Volumes', index=False)
        if len(rds_df) > 0:
            rds_df.to_excel(writer, sheet_name='RDS Instances', index=False)
        if len(aurora_df) > 0:
            aurora_df.to_excel(writer, sheet_name='Aurora Clusters', index=False)
        if len(fsx_windows_df) > 0:
            fsx_windows_df.to_excel(writer, sheet_name='FSx Windows', index=False)
        if len(fsx_lustre_df) > 0:
            fsx_lustre_df.to_excel(writer, sheet_name='FSx Lustre', index=False)
        if len(documentdb_df) > 0:
            documentdb_df.to_excel(writer, sheet_name='DocumentDB', index=False)
        if len(neptune_df) > 0:
            neptune_df.to_excel(writer, sheet_name='Neptune', index=False)
        if len(storage_gateway_df) > 0:
            storage_gateway_df.to_excel(writer, sheet_name='Storage Gateway', index=False)
        if len(s3_df) > 0:
            s3_df.to_excel(writer, sheet_name='S3 Buckets', index=False)

    print(f'\n{"="*80}')
    print(f'Report: {OUTPUT_FILENAME}')
    print(f'Environment: {ENVIRONMENT.upper()}')
    print('RESOURCES TO BACK UP (for cost estimation):')
    if len(dynamodb_df) > 0:
        print(f'DynamoDB: {len(dynamodb_df)} tables, {dynamodb_df["Size (GB)"].sum():.2f} GB')
    if len(efs_df) > 0:
        print(f'EFS: {len(efs_df)} file systems, {efs_df["Size (GB)"].sum():.2f} GB')
    if len(ebs_df) > 0:
        print(f'EBS: {len(ebs_df)} volumes, {ebs_df["Size (GB)"].sum():,.0f} GB')
    if len(rds_df) > 0:
        print(f'RDS: {len(rds_df)} instances, {rds_df["Size (GB)"].sum():,.0f} GB')
    if len(aurora_df) > 0:
        print(f'Aurora: {len(aurora_df)} clusters, {aurora_df["Size (GB)"].sum():,.0f} GB')
    if len(fsx_windows_df) > 0:
        print(f'FSx Windows: {len(fsx_windows_df)} file systems, {fsx_windows_df["Size (GB)"].sum():,.0f} GB')
    if len(fsx_lustre_df) > 0:
        print(f'FSx Lustre: {len(fsx_lustre_df)} file systems, {fsx_lustre_df["Size (GB)"].sum():,.0f} GB')
    if len(documentdb_df) > 0:
        print(f'DocumentDB: {len(documentdb_df)} clusters, {documentdb_df["Size (GB)"].sum():,.0f} GB')
    if len(neptune_df) > 0:
        print(f'Neptune: {len(neptune_df)} clusters, {neptune_df["Size (GB)"].sum():,.0f} GB')
    if len(storage_gateway_df) > 0:
        print(f'Storage Gateway: {len(storage_gateway_df)} volumes, {storage_gateway_df["Size (GB)"].sum():,.2f} GB')
    if len(s3_df) > 0:
        print(f'S3: {len(s3_df)} buckets, {s3_df["Size (GB)"].sum():,.2f} GB')
    print(f'{"="*80}')
    print('\nScript execution completed.')
