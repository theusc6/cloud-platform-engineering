#!/usr/bin/env python3

"""
List users in a GitHub Organization
"""

import argparse
import sys
from datetime import datetime

import requests
from tabulate import tabulate
from github import Github, GithubException

from githubauthlib.github_auth import get_github_token


def main():
    """
    List users in a GitHub Organization
    """
    try:
        # Use the correct keychain for the operating system
        github_token = get_github_token()

        # Create an argument parser
        parser = argparse.ArgumentParser(
            description='List all users in the requested GitHub organization.')
        parser.add_argument(
            '-o', '--organization',
            type=str,
            required=True,
            help='Your GitHub organization.'
        )
        args = parser.parse_args()

        # Create a PyGithub object with the access token
        github = Github(github_token)

        # Get the organization by name
        org = get_organization(github, args.organization)

        # List organization members
        list_organization_members(org, github_token)

    except GithubException as error:
        print(f"An error occurred: {error}")
        sys.exit(1)


def get_organization(github, organization_name):
    """
    Get the organization from GitHub
    """
    try:
        return github.get_organization(organization_name)
    except GithubException as error:
        print(f"Unable to retrieve the organization '{organization_name}' from GitHub.")
        print(f"Error: {error}")
        raise


def get_enterprise_users(github):
    """
    Get all users from GitHub Enterprise using SDK
    """
    try:
        # Get the organization
        org = github.get_organization('theusc6')
        members = org.get_members()

        # Convert to list with needed attributes
        return [{
            'login': member.login,
            'name': member.name,
            'id': member.id
        } for member in members]
    except GithubException as e:
        print(f"Error fetching enterprise users: {e}", file=sys.stderr)
        return []


def get_scim_users(token, org_name):
    """
    Get all SCIM users from the organization
    """
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+scim+json'
    }

    try:
        response = requests.get(
            f'https://api.github.com/scim/v2/organizations/{org_name}/Users',
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json().get('Resources', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching SCIM users: {e}", file=sys.stderr)
        return []


def list_organization_members(org, token):
    """
    List organization members and their statistics
    """
    table_data = []
    headers = ["Username", "Full Name", "Email"]

    # Get all data first using Github instance
    github = Github(token)  # Create Github instance here
    enterprise_users = get_enterprise_users(github)
    scim_users = get_scim_users(token, org.login)

    # Create lookup dictionaries
    enterprise_lookup = create_enterprise_lookup(enterprise_users)
    scim_lookup = create_scim_lookup(scim_users)

    # Match users and build table
    for member in org.get_members():
        try:
            row = create_table_row(member, enterprise_lookup, scim_lookup)
            table_data.append(row)
        except GithubException as error:
            print(f"Error processing member {member.login}: {error}", file=sys.stderr)
            continue

    # Print report
    print_report(org, table_data, headers)


def normalize_name(name):
    """Normalize a name for comparison"""
    if not name:
        return []
    # Convert to lowercase and remove spaces/punctuation
    basic = ''.join(e.lower() for e in name if e.isalnum())
    # Also store first+last name variations
    parts = name.lower().split()
    variations = [basic]

    if len(parts) >= 2:
        first = parts[0]
        last = parts[-1]
        # Only include full name combinations
        variations.extend([
            f"{first}{last}",
            f"{last}{first}"
        ])
        # For names with middle parts, try without them
        if len(parts) > 2:
            variations.append(f"{first}{parts[-1]}")
            variations.append(f"{parts[-1]}{first}")

    return variations


def create_enterprise_lookup(enterprise_users):
    """Create lookup dictionary for enterprise users"""
    enterprise_lookup = {}
    for user in enterprise_users:
        if user.get('name'):
            # Get all name variations
            norm_variations = normalize_name(user['name'])
            for norm_name in norm_variations:
                enterprise_lookup[norm_name] = {
                    'username': user['login'],
                    'name': user['name']
                }
    return enterprise_lookup


def create_scim_lookup(scim_users):
    """Create lookup dictionary for SCIM users"""
    scim_lookup = {}
    for user in scim_users:
        if user.get('name'):
            full_name = f"{user['name']['givenName']} {user['name']['familyName']}"
            # Get all name variations
            norm_variations = normalize_name(full_name)
            for norm_name in norm_variations:
                scim_lookup[norm_name] = {
                    'email': user['userName'],
                    'name': full_name
                }
    return scim_lookup


def create_table_row(member, enterprise_lookup, scim_lookup):
    """Create a table row for a member"""
    # First get enterprise data by username
    for data in enterprise_lookup.values():
        if data['username'].lower() == member.login.lower():
            # Try to find matching SCIM user
            name_variations = normalize_name(data['name'])
            for variation in name_variations:
                if variation in scim_lookup:
                    scim_data = scim_lookup[variation]
                    # Found SCIM data too, return all info
                    return [
                        member.login,
                        scim_data['name'],
                        scim_data['email']
                    ]

            # No SCIM match, but we have enterprise data - use that
            return [
                member.login,
                data['name'],
                'No email available'
            ]

    # No enterprise match found - use GitHub username as the name
    return [
        member.login,
        member.login,
        'No email available'
    ]


def print_report(org, table_data, headers):
    """Print the final report"""
    print("\nGitHub Organization Members Report")
    print(f"Organization: {org.login}")
    print(f"Licensed Users: {len(table_data)} (of 150 available licenses)")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    print(tabulate(
        table_data,
        headers=headers,
        tablefmt="grid",
        numalign="center",
        stralign="left"
    ))
    print(f"\nTotal Members: {len(table_data)}")


if __name__ == "__main__":
    main()
