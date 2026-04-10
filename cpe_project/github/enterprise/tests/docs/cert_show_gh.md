# GitHub Enterprise CA Certificate Viewer Script

This script is designed to retrieve and display the current CA (Certificate Authority) certificate on a GitHub Enterprise server. It utilizes the GitHub CLI (`gh`) to query the server for the SSL CA certificate settings and then displays the retrieved certificate.

**Author:** user

## Overview

This script simplifies the process of viewing the current CA certificate installed on a GitHub Enterprise server. It employs the GitHub CLI (`gh`) to make an API request to retrieve the SSL CA certificate. The following configuration parameter must be specified:

- `BASE_URL`: The base URL of your GitHub Enterprise instance.

## How to Use

1. Replace the `BASE_URL` placeholder in the script with the base URL of your GitHub Enterprise instance.

2. Run the script using a Python interpreter.

## Script Execution

The script performs the following steps:

1. Executes the specified `gh` command to retrieve the SSL CA certificate information.
2. Checks the output status of the executed command:
   - If the status code is 0, indicating success, the script proceeds to parse the response.
   - If the status code is not 0, it indicates a failure and an error message is displayed.

3. If the SSL CA certificate is found in the response JSON:
   - The script extracts and prints the certificate.
   - If no SSL CA certificate is found, a message indicating the absence is displayed.

## Note

The script uses the GitHub CLI (`gh`) to interact with the GitHub Enterprise server. Make sure you have the `gh` tool installed and configured correctly before using this script. Additionally, the script assumes you have the necessary permissions to retrieve the SSL CA certificate.

---

Remember to replace the `BASE_URL` placeholder with your actual GitHub Enterprise base URL. The script provides a straightforward way to quickly view the current SSL CA certificate configured on your GitHub Enterprise server.
