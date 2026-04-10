#!/usr/bin/env python3

"""
Create an GitHub.com Organization Archive and send it to S3
# https://docs.github.com/en/rest/migrations/orgs#download-an-organization-migration-archive
"""

import os
import sys
import argparse
from datetime import datetime
import boto3
import requests
from tqdm import tqdm
from botocore.exceptions import NoCredentialsError
from githubauthlib.github_auth import get_github_token

def parse_arguments():
    """ 
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(
        description='Create an Organization Archive from GitHub.com and export to AWS S3.')
    parser.add_argument('-p', '--profile', required=True, help='AWS profile name for SSO login')
    return parser.parse_args()

def download_archive(url, filename, token, timeout=10):
    """
    Download a file from a URL and save it to a local file
    """
    response = None
    try:
        response = requests.get(
            url, stream=True, headers={'Authorization': f'token {token}'}, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        print(f"Failed to download {url}: {error}")
        if response:
            print(f"Response content: {response.content}")
        return

    with open(filename, 'wb') as file:
        for chunk in tqdm(response.iter_content(chunk_size=8192),
                          desc="Downloading", unit="B", unit_scale=True, unit_divisor=1024):
            file.write(chunk)

def upload_to_s3(local_file, s3_file, profile, bucket_name):
    """
    Upload a file to an S3 bucket
    """
    session = boto3.Session(profile_name=profile)
    sss = session.client('s3')

    try:
        sss.upload_file(local_file, bucket_name, s3_file)
        print(f"Upload Successful: {s3_file}")
        return True
    except FileNotFoundError:
        print(f"The file {local_file} was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

def fetch_and_archive_repos(github_token, org_name):
    """
    Fetch all repos from an org and archive them
    """
    page = 1
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    local_filename = f'{org_name}_archive_{timestamp}.zip'
    repo_names = []

    while True:
        archive_url = f'https://api.github.com/orgs/{org_name}/repos?per_page=100&page={page}'
        try:
            response = requests.get(
                archive_url, headers={'Authorization': f'token {github_token}'}, timeout=10)
            response.raise_for_status()

            repos = response.json()
            if not repos:
                break

            for repo in repos:
                repo_names.append(repo['name'])
                download_url = repo['archive_url'].replace(
                    '{archive_format}', 'zipball').replace('{/ref}', '')
                download_archive(download_url, f"{repo['name']}.zip", github_token)

            page += 1
        except requests.exceptions.RequestException as error:
            print(f"Failed to fetch repositories from {archive_url}: {error}")
            break

    return repo_names, local_filename

def create_final_archive(repo_names, local_filename):
    """
    Create a final archive file from all the individual repo archives
    """
    with open(local_filename, 'wb') as file_name:
        for repo_name in repo_names:
            try:
                with open(f"{repo_name}.zip", 'rb') as file:
                    file_name.write(file.read())
                os.remove(f"{repo_name}.zip")
            except FileNotFoundError:
                print(f"File {repo_name}.zip not found")

    return local_filename

def main(args):
    """
    Main function
    """
    org_name = 'theusc6'
    s3_bucket_name = 'myorg-github-archives'  # this must exist BEFORE you run this script
    aws_profile = args.profile

    print('Getting Github token...')
    github_token = get_github_token()
    if not github_token:
        print('Unable to get Github token')
        sys.exit(1)

    repo_names, local_filename = fetch_and_archive_repos(github_token, org_name)

    # Create the final archive
    final_archive = create_final_archive(repo_names, local_filename)

    # Print total number of repos and number of repos in the archive file
    print(f"\nTotal repos in org: {len(repo_names)}")
    print(f"Total repos in archive: {len(repo_names)}\n")

    # Upload the final archive to S3
    print(f"Uploading {final_archive} to S3 {s3_bucket_name} bucket...")
    if upload_to_s3(final_archive, final_archive, aws_profile, s3_bucket_name):
        print("Removing local file...")
        os.remove(final_archive)
    else:
        print("Failed to upload to S3. Local file not removed.")

if __name__ == '__main__':
    args = parse_arguments()
    main(args)
