# Security Hub Findings Exporter

This script allows you to export AWS Security Hub findings to an XLSX file, optionally filtered by severity level.

## Usage

1. Install the required Python packages by running:

   ```sh
   pip install boto3 pandas
   ```

2. Run the script using the following command:

   ```sh
   python local_export_security_hub_findings.py -p <AWS_PROFILE_NAME> [-s SEVERITY]
   ```

   Replace `<AWS_PROFILE_NAME>` with the name of your AWS profile.

3. Optional: Use the `-s` or `--severity` flag followed by the severity level to filter findings based on severity. Supported severity levels are: `INFORMATIONAL`, `LOW`, `MEDIUM`, `HIGH`, and `CRITICAL`.

## Example

To export all findings with severity `HIGH` using the AWS profile `my_profile`:

```sh
python local_export_security_hub_findings.py -p my_profile -s HIGH
```

## What It Does

1. Parses command-line arguments to specify the AWS profile and optional severity filter.

2. Retrieves Security Hub findings using the specified AWS profile.

3. Optionally filters findings based on severity level.

4. Converts the findings to a Pandas DataFrame.

5. Creates an `exports` directory if it doesn't exist.

6. Generates a timestamp and saves the findings in an XLSX file named `security_hub_findings_<timestamp>.xlsx` within the `exports` directory.

7. Calculates and prints the elapsed time of execution.

This script simplifies the process of exporting Security Hub findings, allowing you to efficiently analyze and share important security information.
