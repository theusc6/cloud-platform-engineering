"""
This module exports all Dependabot alerts from GitHub, including the Dependency Scope.

"""

import re
import csv
from datetime import datetime
import requests
from githubauthlib.github_auth import get_github_token

# Constants and Global Variables
API_URL = "https://api.github.com/graphql"
ORG_NAME = "theusc6"

# Use the correct keychain for the operating system
github_token = get_github_token()

headers = {
    "Authorization": f"Bearer {github_token}",
    "Content-Type": "application/json",
}

# Fetch all repositories
QUERY_REPOSITORIES = """
query($orgName: String!, $after: String) {
  organization(login: $orgName) {
    repositories(first: 100, after: $after) {
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        name
      }
    }
  }
}
"""

HAS_NEXT_PAGE = True
END_CURSOR = None
ALL_REPOS = []

while HAS_NEXT_PAGE:
    variables = {
        "orgName": ORG_NAME,
        "after": END_CURSOR
    }
    response = requests.post(
        API_URL,
        headers=headers,
        json={
            "query": QUERY_REPOSITORIES,
            "variables": variables
        },
        timeout=5
    )
    if response.status_code == 200:
        data = response.json()
        if 'data' in data:
            organization = data['data']['organization']
            if organization is not None and 'repositories' in organization:
                repos_data = organization['repositories']
                if repos_data is not None and 'nodes' in repos_data:
                    repos = repos_data['nodes']
                    ALL_REPOS.extend(repos)
                    page_info = repos_data['pageInfo']
                    HAS_NEXT_PAGE = page_info['hasNextPage']
                    END_CURSOR = page_info['endCursor']
                else:
                    print("Error: 'nodes' field is missing in the repositories data")
            else:
                print("Error: 'repositories' field is missing in the organization data")
        else:
            print("Error: 'data' field is missing in the response")
    else:
        print(f"Error retrieving repositories: {response.status_code}")

# Fetch Dependabot alerts
QUERY_ALERTS = """
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    vulnerabilityAlerts(first: 100) {
      edges {
        node {
          id
          vulnerableManifestPath
          vulnerableRequirements
          createdAt
          dismissedAt
          securityVulnerability {
            package {
              name
            }
            severity
            updatedAt
            vulnerableVersionRange
          }
        }
      }
    }
  }
}
"""

all_alerts_data = []

for repo in ALL_REPOS:
    variables = {
        "owner": ORG_NAME,
        "name": repo['name']
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json={
            "query": QUERY_ALERTS,
            "variables": variables
        },
        timeout=5
    )

    if response.status_code == 200:
        data = response.json()
        vulnerability_alerts = data['data']['repository']['vulnerabilityAlerts']['edges']

        for alert in vulnerability_alerts:
            node = alert['node']
            package = node['securityVulnerability']['package']
            vulnerable_requirements = node['vulnerableRequirements']

            # Logic to capture Dependency Scope
            scope_matches = re.search(r'scope\s*:\s*([^\s,]+)',
                                      vulnerable_requirements, re.IGNORECASE)
            scope = scope_matches.group(1) if scope_matches else "N/A"

            alert_data = {
                "repository": repo['name'],
                "alert_id": node['id'],
                "package_name": package['name'],
                "vulnerableManifestPath": node['vulnerableManifestPath'],
                "vulnerableRequirements": node['vulnerableRequirements'],
                "vulnerability_severity": node['securityVulnerability']['severity'],
                "created_at": node['createdAt'],
                "updated_at": node['securityVulnerability']['updatedAt'],
                "dismissed_at": node['dismissedAt'],
                "dependency_scope": node.get('dependencyScope', 'N/A')
            }
            all_alerts_data.append(alert_data)
    else:
        print(f"Error retrieving alerts for {repo['name']}: {response.status_code}")

# Export to CSV
csv_columns = [
    "repository",
    "dependency_scope",
    "alert_id",
    "package_name",
    "vulnerableManifestPath",
    "vulnerableRequirements",
    "vulnerability_severity",
    "created_at",
    "updated_at",
    "dismissed_at"
]

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
csv_file = f'dependabot_alerts_{timestamp}.csv'

try:
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in all_alerts_data:
            writer.writerow(data)
except IOError:
    print("I/O error occurred while writing to CSV file")

print(f"Exported Dependabot alerts for {len(ALL_REPOS)} repositories to {csv_file}")
