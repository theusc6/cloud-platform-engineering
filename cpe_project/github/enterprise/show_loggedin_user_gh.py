#!/usr/bin/env python3

"""
A script that shows the logged in user on a GitHub Enterprise server.

"""

import subprocess
import json
import sys

try:
    # Execute the gh command to get user information
    user_info_command = ["gh", "api", "/user"]
    user_info_output = subprocess.run(user_info_command, capture_output=True, text=True, check=True)

    # Check the output status
    if user_info_output.returncode == 0:
        response_json = json.loads(user_info_output.stdout)

        # Extract user information
        username = response_json["login"]
        name = response_json["name"]
        email = response_json["email"]
        bio = response_json["bio"]
        followers = response_json["followers"]
        following = response_json["following"]
        public_repos = response_json["public_repos"]
        company = response_json["company"]
        location = response_json["location"]
        created_at = response_json["created_at"]

        print("User Information:")
        print(f"Username: {username}")
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Bio: {bio}")
        print(f"Followers: {followers}")
        print(f"Following: {following}")
        print(f"Public Repositories: {public_repos}")
        print(f"Company: {company}")
        print(f"Location: {location}")
        print(f"Account Created At: {created_at}")
    else:
        print("Failed to retrieve user information.")
        print("Error:", user_info_output.stderr)
except subprocess.CalledProcessError as e:
    print("Error occurred while retrieving user information:", e)
except KeyboardInterrupt:
    sys.exit(0)
