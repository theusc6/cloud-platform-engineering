"""
A script to start a service software update for an Amazon OpenSearch domain.

This script allows the user to initiate a service software update
for a specified OpenSearch domain in their AWS account.

Command line arguments:
    -p, --profile: (required) AWS profile name for SSO login
    -d, --domain: (required) Name of the OpenSearch domain

Example usage:
    python3 script_name.py --profile my_profile --domain my_domain


"""

import argparse
import boto3
from botocore.exceptions import ClientError

def start_software_update(opensearch_client, domain_name, update_time):
    """
    Starts a service software update for the specified OpenSearch domain.

    Parameters:
        opensearch_client (botocore.client.OpenSearch): The OpenSearch client.
        domain_name (str): The name of the OpenSearch domain.

    Raises:
        botocore.exceptions.ClientError: If an error occurs while trying to start the update.
    """
    try:
        opensearch_client.start_service_software_update(
            DomainName=domain_name,
            ScheduleAt=update_time)
        print(f"Started service software update for domain {domain_name}.")
    except ClientError as error:
        print(f"An error occurred while starting service software update: "
              f"{error.response['Error']['Message']}")

def get_update_time():
    """
    This function returns user input for the update time. Specifies either 
    an immediate update (if there is available capacity) or on the next 
    upcoming off-peak window. 
    
    Note: There’s no guarantee that the update will happen during the
    next immediate window. Depending on capacity, it might happen in subsequent days.
    """
    user_input = input("Please enter the desired update time. Please "
                       "choose either 'NOW' or 'OFF_PEAK_WINDOW': ")
    return user_input

def main():
    """
    Parses command-line arguments, establishes an AWS session,
    and starts a service software update for an OpenSearch domain.
    """
    parser = argparse.ArgumentParser(description="Start OpenSearch Service Software Update")
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('-d', '--domain', required=True, type=str,
                        help='Name of the OpenSearch domain')

    args = parser.parse_args()

    session = boto3.Session(profile_name=args.profile)
    opensearch_client = session.client('opensearch')

    update_time = get_update_time()

    start_software_update(opensearch_client, args.domain, update_time)

if __name__ == "__main__":
    main()
