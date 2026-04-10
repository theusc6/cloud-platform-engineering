#!/usr/bin/env python3

"""
This module exports tagged Dependabot alerts by Topic from GitHub.

"""

import csv
from datetime import datetime
import requests
from githubauthlib.github_auth import get_github_token

github_token = get_github_token()
API_URL = "https://api.github.com/graphql"
ORG_NAME = "theusc6"

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
        repositoryTopics(first: 100) {
          nodes {
            topic {
              name
            }
          }
        }
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
                print(response.content)
        else:
            print("Error: 'data' field is missing in the response")
            print(response.content)
    else:
        print(f"Error retrieving repositories: {response.status_code}")
        print(response.content)

# Fetch Dependabot alerts for each repository
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
repo_alerts_count = {}  # Store alerts count for each repo
REPOS_WITH_ALERTS = 0  # Count of repos with alerts

for repo in ALL_REPOS:
    repo_topics = [topic_node['topic']['name'] for topic_node in repo['repositoryTopics']['nodes']]
    if 'production-code' in repo_topics:
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

            if len(vulnerability_alerts) > 0:
                REPOS_WITH_ALERTS += 1
                repo_alerts_count[repo['name']] = len(vulnerability_alerts)

            for alert in vulnerability_alerts:
                node = alert['node']
                package = node['securityVulnerability']['package']
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
                    "topics": ', '.join(repo_topics)  # This adds the list of topics to the CSV
                }
                all_alerts_data.append(alert_data)
        else:
            print(f"Error retrieving alerts for {repo['name']}: {response.status_code}")
            print(response.content)

# Reporting on repositories and alerts
print(f"\nFound {REPOS_WITH_ALERTS} repositories with 'production-code' topic having alerts.")
for repo_name, alerts_count in repo_alerts_count.items():
    print(f"Repository '{repo_name}' has {alerts_count} alerts.")

csv_columns = [
    "repository",
    "alert_id",
    "package_name",
    "vulnerableManifestPath",
    "vulnerableRequirements",
    "vulnerability_severity",
    "created_at",
    "updated_at",
    "dismissed_at",
    "topics"  # I added this column to the CSV
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
    print("I/O error writing to CSV file")

print(f"Exported Dependabot alerts for {len(ALL_REPOS)} repositories to {csv_file}")
