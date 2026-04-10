#!/usr/bin/env python3

"""
A script that shows the CA certificate on a GitHub Enterprise server.

"""

import subprocess
import json

# Configuration
BASE_URL = "https://github.example.com"

# Command to retrieve SSL CA certificate using gh
GET_CERT_COMMAND = ["gh", "api", "/admin/settings/ssl_ca_certificate"]

try:
    # Execute the gh command
    get_cert_output = subprocess.run(GET_CERT_COMMAND, capture_output=True, text=True, check=True)

    # Check the output status
    if get_cert_output.returncode == 0:
        response_json = json.loads(get_cert_output.stdout)
        if "certificate" in response_json:
            certificate = response_json["certificate"]
            print("Current SSL CA Certificate:")
            print(certificate)
        else:
            print("No SSL CA certificate found.")
    else:
        print("Failed to retrieve the SSL CA certificate.")
        print("Error:", get_cert_output.stderr)
except subprocess.CalledProcessError as error:
    print("Error occurred while retrieving the SSL CA certificate:", error)
