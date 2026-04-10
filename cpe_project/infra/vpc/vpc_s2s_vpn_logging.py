import argparse
import boto3
from botocore.exceptions import ClientError
import time

def parse_args():
    """
    Parse command-line arguments passed to the script.
    """
    parser = argparse.ArgumentParser(
        description='Enable CloudWatch logging for both tunnels of a Site-to-Site VPN connection.'
    )
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name for authentication')
    parser.add_argument('-r', '--region', required=True, type=str,
                        help='AWS region where the VPN connection is located')
    parser.add_argument('-v', '--vpn', required=True, type=str,
                        help='VPN Connection ID')
    return parser.parse_args()

def wait_for_vpn_available(vpn_connection_id, ec2_client):
    """
    Wait until the VPN connection is in 'available' state.
    """
    print(f"Waiting for VPN connection {vpn_connection_id} to be in 'available' state.")
    while True:
        response = ec2_client.describe_vpn_connections(VpnConnectionIds=[vpn_connection_id])
        vpn_state = response['VpnConnections'][0]['State']
        if vpn_state == 'available':
            print(f"VPN connection {vpn_connection_id} is now available.")
            break
        else:
            print(f"VPN connection {vpn_connection_id} is in '{vpn_state}' state. Retrying in 180 seconds.")
            time.sleep(180)

def enable_vpn_logging(vpn_connection_id, cloudwatch_log_group, ec2_client):
    """
    Enable logging for both tunnels of a given VPN connection.

    Parameters:
    vpn_connection_id (str): The ID of the VPN connection.
    cloudwatch_log_group (str): The CloudWatch Log Group to use for logging.
    ec2_client (boto3.client): Boto3 EC2 client object.
    """
    try:
        # Describe the VPN connection to retrieve the tunnels
        vpn_connection = ec2_client.describe_vpn_connections(VpnConnectionIds=[vpn_connection_id])
        tunnels = vpn_connection['VpnConnections'][0]['Options']['TunnelOptions']

        # Enable logging for each tunnel
        for tunnel_index, tunnel in enumerate(tunnels, start=1):
            outside_ip = tunnel.get('OutsideIpAddress')
            print(f"Enabling logging for Tunnel {tunnel_index} with outside IP: {outside_ip}")
            ec2_client.modify_vpn_tunnel_options(
                VpnConnectionId=vpn_connection_id,
                VpnTunnelOutsideIpAddress=outside_ip,
                TunnelOptions={
                    'LogOptions': {
                        'CloudWatchLogOptions': {
                            'LogEnabled': True,
                            'LogGroupArn': cloudwatch_log_group,
                            'LogOutputFormat': 'json'  # Or specify 'text' if preferred
                        }
                    }
                }
            )
            print(f"Logging enabled for Tunnel {tunnel_index} of VPN connection {vpn_connection_id} with outside IP: {outside_ip}.")
            
            # Wait for VPN connection to become 'available' before modifying the next tunnel
            wait_for_vpn_available(vpn_connection_id, ec2_client)

    except ClientError as error:
        print(f"An error occurred while enabling logging: {error.response['Error']['Message']}")

def main():
    """
    Main function of the script.
    """
    args = parse_args()
    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    ec2_client = session.client('ec2')
    logs_client = session.client('logs')

    # Get account ID to construct the ARN
    sts_client = session.client('sts')
    account_id = sts_client.get_caller_identity().get('Account')

    # Construct the CloudWatch Log Group ARN
    cloudwatch_log_group_name = f"/aws/vpn/{args.vpn}"
    cloudwatch_log_group_arn = f"arn:aws:logs:{args.region}:{account_id}:log-group:{cloudwatch_log_group_name}"

    # Create the CloudWatch Log Group if it doesn't exist
    try:
        logs_client.create_log_group(logGroupName=cloudwatch_log_group_name)
        print(f"Created CloudWatch Log Group: {cloudwatch_log_group_name}")
    except ClientError as error:
        if error.response['Error']['Code'] == 'ResourceAlreadyExistsException':
            print(f"Log group {cloudwatch_log_group_name} already exists.")
        else:
            print(f"An error occurred while creating the log group: {error.response['Error']['Message']}")

    # Enable logging for the VPN connection
    enable_vpn_logging(args.vpn, cloudwatch_log_group_arn, ec2_client)

if __name__ == "__main__":
    main()