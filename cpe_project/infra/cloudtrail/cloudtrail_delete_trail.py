"""
This script deletes a specific AWS CloudTrail trail.

Usage: python3 delete_cloudtrail.py --profile <profile_name> --trail <trail_name>
"""
import argparse
import boto3
from botocore.exceptions import ClientError

def parse_args():
    """
    Parse command-line arguments passed to the script.
    """
    parser = argparse.ArgumentParser(
        description='Delete a CloudTrail trail.'
    )
    parser.add_argument('-p', '--profile', required=True, type=str,
                        help='AWS profile name for SSO login')
    parser.add_argument('-t', '--trail', required=True, type=str,
                        help='CloudTrail trail name')
    parser.add_argument('-r', '--region', required=True, type=str,
                        help='AWS region for the trail') # Added region argument
    return parser.parse_args()

def delete_cloudtrail(cloudtrail, trail_name):
    """
    Delete the specified CloudTrail trail.
    """
    try:
        cloudtrail.delete_trail(
            Name=trail_name
        )
        print(f"Success! Deleted CloudTrail trail '{trail_name}'.")
    except ClientError as client_error:
        error_message = client_error.response['Error']['Message']
        error_code = client_error.response['Error']['Code']

        if error_code == 'TrailNotFoundException':
            print(f'A TrailNotFoundException occurred. It seems that the trail '
                  f'cannot be found.'
                  f'Error Message: {error_message}')

        elif error_code == "InvalidTrailNameException":
            print(f'An InvalidTrailNameException occurred. It seems that the trail '
                  f'entered is invalid.'
                  f'Error Message: {error_message}')

        elif error_code == "InvalidHomeRegionException":
            print(f'An InvalidHomeRegionException occurred. It seems that an '
                  f'invalid region has been entered.'
                  f'Error Message: {error_message}')

        elif error_code == "UnsupportedOperationException":
            print(f'An UnsupportedOperationException occurred. It seems that an '
                  f'this operation is not supported.'
                  f'Error Message: {error_message}')

def main():
    """
    Main function of the script.
    """
    args = parse_args()
    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    cloudtrail = session.client('cloudtrail')

    delete_cloudtrail(cloudtrail, args.trail)

if __name__ == "__main__":
    main()
