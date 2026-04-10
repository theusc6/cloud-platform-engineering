# Enable CloudWatch Logging for VPN Tunnels

This script enables Amazon CloudWatch logging for both tunnels of a specified AWS Site-to-Site VPN connection. By running this script, you can ensure that each VPN tunnel’s traffic is logged to CloudWatch, with separate log streams created for each tunnel based on its outside IP address.

## Usage


`python3 enable_vpn_logging.py -p <profile_name> -r <region_name> -v <vpn_connection_id>`

## Argument Parsing

The script expects three command-line arguments:

- `-p` or --profile: The AWS profile name to use for authentication.
- `-r` or --region: The AWS region where the VPN connection is located.
- `-v` or --vpn: The ID of the VPN connection for which CloudWatch logging should be enabled.



Exception Handling: If any error occurs during the execution, it is caught and displayed to the user.

## Dependencies
- boto3
- botocore

Ensure that you have these libraries installed in your environment before executing the script.

## Log Group and Log Stream Structure

The logs for each tunnel are stored in the same CloudWatch log group with separate log streams for each tunnel. The naming convention is as follows:

	•	Log Group: /aws/vpn/{vpn_connection_id}
	•	Log Stream per Tunnel: {vpn_connection_id}-tunnel-{tunnel_index}-{outside_ip_address}

Example Log Group and Stream Structure

For a VPN connection with ID vpn-abc123 and two tunnels, the log structure will be:

	•	Log Group: /aws/vpn/vpn-abc123
    	   - Log Stream for Tunnel 1: vpn-abc123-tunnel-1-203.0.113.1
		   - Log Stream for Tunnel 2: vpn-abc123-tunnel-2-198.51.100.2

## Exception Handling

If an error occurs during any part of the script (e.g., log group creation or modifying VPN tunnel options), it will be caught and displayed for easier debugging.