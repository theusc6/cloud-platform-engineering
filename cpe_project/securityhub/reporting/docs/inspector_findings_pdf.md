# Inspector Findings Report Generator

This Python script retrieves and aggregates Amazon Inspector findings from the Security Tooling account and generates a PDF report. It provides a summary of findings by severity, account, and region, making it easier to analyze and present security posture.

## Features

- Retrieves Inspector findings from a specified AWS region or all regions.
- Aggregates findings by severity, account ID, and region.
- Includes account names in the report by querying AWS Organizations.
- Sorts accounts in the report by the number of findings in descending order.
- Generates a PDF report with tables and lists for easy visualization.
- Handles `AccessDeniedException` gracefully and skips regions where access is denied.

## Prerequisites

- **Python 3.7 or higher:** Make sure you have a compatible Python version installed.
- **Boto3:** Install the AWS SDK for Python using `pip install boto3`.
- **pdfkit**: Install pdfkit using `pip install pdfkit`.
- **wkhtmltopdf:** Install brew list wkhtmltopdf using **brew** `brew install wkhtmltopdf`.
- **AWS Credentials:** Configure an AWS CLI profile with appropriate credentials to access the Security Tooling account. The profile name should be passed to the script using the `--profile` argument.
- **Amazon Inspector:** Ensure that Amazon Inspector V2 is enabled in the accounts and regions you want to collect findings from.
- **AWS Organizations:** If you want to include account names in the report, the script needs access to AWS Organizations to retrieve account information.

## Usage

1. **Save the script:** Save the script as a Python file (e.g., `inspector_findings_pdf.py`).

2. **Run the script:** Use the following command to run the script:

```bash
python3 inspector_findings_pdf.py --profile <profile_name> [--region <region> | --all-regions]
```

`--profile` <profile_name>: Required. The name of the AWS CLI profile configured for the Security Tooling account.
`--region` <region>: Optional. The AWS region to query. Defaults to us-west-2.
`--all-regions`: Optional. If set, the script will query all available AWS regions.

Example:

To generate a report for all regions using the profile `security-tooling`, run the following:

Login using the profile `security-tooling`

```Bash
aws sso login --profile security-tooling
```

View the `help` menu for the script:

```Bash
$ python3 inspector_findings.py -h
usage: inspector_findings_pdf.py [-h] --profile PROFILE [--region REGION] [--all-regions]

Retrieve and aggregate Inspector findings from Security Tooling account.

options:
  -h, --help         show this help message and exit
  --profile PROFILE  AWS profile name for the Security Tooling account
  --region REGION    AWS region (default: us-west-2). Use 'all' to query all regions.
  --all-regions      If set, query all regions
```

Execute the script

```Bash
python3 inspector_findings_pdf.py --profile security-tooling --all-regions
```

## View the report

The script will generate an HTML report (e.g., `inspector_findings_report_all-regions_20241023_002245.pdf`) in the same directory. Open the report to view the findings summary.

[example AWS Inspector report](docs/img/inspector_findings_report_all-regions_20241023_002245.pdf)

### Error Handling

The script handles AccessDeniedException gracefully. If it encounters this exception while querying a region, it will print a message indicating that the region is being skipped and continue with other regions.

### Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please feel free to open an issue or submit a pull request.

### License

This script is released under the MIT License.
