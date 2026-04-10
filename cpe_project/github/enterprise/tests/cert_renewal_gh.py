#!/usr/bin/env python3

"""
A script that installs a new CA certificate on a GitHub Enterprise server.

"""

import subprocess

# Configuration
BASE_URL = "github.example.com"
CA_CERT_FILE = "<path-to-your-ca-cert.pem>"

# Check if logged in using gh
AUTH_STATUS_COMMAND = "gh auth status --json"
auth_status_output = subprocess.run(
    AUTH_STATUS_COMMAND, shell=True, capture_output=True, text=True, check=True)

# Check the authentication status
if auth_status_output.returncode == 0:
    print("You are logged in. Proceeding with the certificate installation.")
    # Install SSL CA certificate using gh
    install_command = (
    f"gh api -X PUT /admin/settings/ssl_ca_certificate"
    f" --field certificate=@{CA_CERT_FILE}"
    f" -H Accept:application/vnd.github.v3+json"
    f" -H 'Content-Type:application/json' {BASE_URL}"
)
    subprocess.run(install_command, shell=True, check=True)
else:
    print("You are not logged in. Please log in using `gh auth login`.")
