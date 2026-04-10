# GitHub Enterprise CA Certificate Installation Script

This script is designed to install a new CA (Certificate Authority) certificate on a GitHub Enterprise server. It utilizes the GitHub API to send a PUT request with the new certificate to the appropriate endpoint.

**Author:** user

## Overview

This script automates the process of installing a new CA certificate onto a GitHub Enterprise server. It uses the GitHub API to update the SSL CA certificate settings. Before running the script, make sure you have the necessary information and files ready:

- `BASE_URL`: The base URL of your GitHub Enterprise instance.
- `ACCESS_TOKEN`: Your personal access token with appropriate permissions.
- `CA_CERT_FILE`: The path to the CA certificate file (in PEM format) you want to install.

## How to Use

1. Replace the placeholders in the script with your specific configuration:
   - `BASE_URL`: Replace with the base URL of your GitHub Enterprise instance.
   - `ACCESS_TOKEN`: Replace with your personal access token.
   - `CA_CERT_FILE`: Replace with the path to your CA certificate file.

2. Run the script using a Python interpreter.

## Script Execution

The script performs the following steps:

1. Reads the contents of the specified CA certificate file.
2. Constructs the necessary headers with authentication.
3. Constructs the payload containing the CA certificate.
4. Makes an API request to update the SSL CA certificate settings on the GitHub Enterprise server.
5. Checks the response status code:
   - If the status code is 200, the certificate installation is successful.
   - If the status code is not 200, the certificate installation has failed.

Please note that this script is designed for GitHub Enterprise instances and requires an appropriate personal access token with sufficient permissions.

---

Remember to replace placeholders such as `<your-access-token>` and `<path-to-your-ca-cert.pem>` with your actual access token and CA certificate file path. You can further customize and adapt this script to your specific requirements.
