#!/usr/bin/env python3

"""
A script that installs a new CA certificate on a GitHub Enterprise server.

"""

import requests

# Configuration
BASE_URL = "https://github.example.com//api/v3"
ACCESS_TOKEN = "<your-access-token>"
CA_CERT_FILE = "<path-to-your-ca-cert.pem>"

# API endpoint
url = f"{BASE_URL}/enterprise/settings/ssl_ca_certificate"

# Read the CA certificate file
with open(CA_CERT_FILE, "r", encoding="utf-8") as file:
    ca_cert = file.read()

# Create headers with authentication
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Create payload with the CA certificate
payload = {
    "certificate": ca_cert
}

# Make the API request with a timeout
response = requests.put(url, headers=headers, json=payload, timeout=30)


# Check the response status
if response.status_code == 200:
    print("Certificate installation successful.")
else:
    print("Certificate installation failed.")
    print("Response:", response.text)
