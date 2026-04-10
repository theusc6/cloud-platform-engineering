# GitHub Enterprise CA Certificate Installer

This script automates the process of installing a new Certificate Authority (CA) certificate on a GitHub Enterprise server. It uses the GitHub CLI tool (`gh`) to interact with the GitHub Enterprise API and configure the SSL CA certificate.

## Usage

1. Make sure you have the GitHub CLI (`gh`) tool installed and configured with the appropriate authentication.

2. Configure the script by modifying the variables in the script according to your environment:

    - `BASE_URL`: The base URL of your GitHub Enterprise server.
    - `CA_CERT_FILE`: The path to the PEM-encoded CA certificate file.

3. Run the script using the following command:

    ```python
    python install_ca_certificate.py
    ```

4. The script will first check if you are logged in using `gh auth status`. If you are logged in, it will proceed with the certificate installation. If not, it will prompt you to log in using `gh auth login`.

5. Once authenticated, the script will send a PUT request to install the specified CA certificate on the GitHub Enterprise server using the GitHub API.

## About

This script was written by user to simplify the process of installing CA certificates on GitHub Enterprise servers.

For more information on the GitHub CLI (`gh`), refer to the official documentation: [GitHub CLI Documentation](https://cli.github.com/manual/)

For any issues or improvements related to this script, feel free to contribute to the repository or contact the author.
