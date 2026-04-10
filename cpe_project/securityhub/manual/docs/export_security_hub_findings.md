# Security Hub Findings Export Script

This script is designed to export AWS Security Hub findings to an XLSX file, providing you with a convenient way to analyze and manage security-related information. The script supports exporting findings either to a local XLSX file or to an Amazon S3 bucket, based on your preferred export option.

## Prerequisites

- Python 3.x installed on your system.
- AWS CLI configured with valid credentials and a named profile.

## Installation

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/yourusername/security-hub-export-script.git
   ```

2. Install the required Python packages using pip:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the script with the following command:

```bash
python export_security_hub_findings.py -p <AWS_PROFILE_NAME> -e <EXPORT_OPTION> [-s <SEVERITY_LEVEL>]
```

Replace `<AWS_PROFILE_NAME>` with the name of your AWS CLI profile, `<EXPORT_OPTION>` with either "local" or "s3" based on where you want to export the findings, and `<SEVERITY_LEVEL>` with an optional severity level ("INFORMATIONAL", "LOW", "MEDIUM", "HIGH", "CRITICAL") to filter findings by severity.

### Examples

Export findings to a local XLSX file:

```bash
python export_security_hub_findings.py -p my-profile -e local -s HIGH
```

Export findings to an S3 bucket:

```bash
python export_security_hub_findings.py -p my-profile -e s3
```

## Output

- If exporting locally, the script creates an "exports" directory (if it doesn't exist) and saves the findings as an XLSX file with a timestamp.
- If exporting to S3, the script creates a bucket and folder (if they don't exist) and uploads the XLSX file to the specified location.
