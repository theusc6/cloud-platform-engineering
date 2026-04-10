# AWS Organization Region Analyzer

## Overview

The **AWS Organization Region Analyzer** is a Python script designed to analyze Service Control Policies (SCPs) in an AWS Organization. It identifies all regions referenced in `aws:RequestedRegion` conditions, helping you understand which regions are being controlled or restricted across the organization's SCPs.

### Key Features:
- Retrieves all SCPs in the AWS Organization.
- Extracts `aws:RequestedRegion` values from each SCP.
- Aggregates and displays unique regions in a sorted list.

This tool is particularly useful for AWS administrators who need to audit or manage region restrictions across multiple accounts in an organization.

---

## Why Was This Script Created?

AWS Organizations allow administrators to enforce policies across accounts using SCPs. These policies can include conditions that restrict or allow access to specific AWS regions. However, there is no built-in AWS CLI or console feature to aggregate and analyze these region restrictions across all SCPs. This script was created to fill that gap by:
1. Automating the retrieval of SCPs.
2. Parsing and extracting region-related conditions.
3. Providing a clear, deduplicated list of regions referenced in the policies.

---

## Prerequisites

Before using this script, ensure you have the following:
1. **Python 3.9 or later** installed on your system.
2. **Boto3** Python library installed (used to interact with AWS services).
3. **AWS CLI profile** configured with sufficient permissions:
   - `organizations:ListPolicies`
   - `organizations:DescribePolicy`

---

## How to Use the Script

### Step 1: Clone the Repository
First, clone the repository containing the script:
```bash
git clone https://github.com/theusc6/cloud-platform-engineering.git
```

### Step 2: Change into the Correct Directory
Navigate to the directory containing the script:

```bash
cd cloud-platform-engineering/cpe_project/queries/organization_level
```

### Step 3: Create and Activate a Python Virtual Environment
It is recommended to use a virtual environment to manage dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Required Dependencies
Install the required Python libraries:

```python
pip install boto3
```

### Step 5: Run the Script
Run the script with the appropriate AWS CLI profile:

```python
python us_all_enabled_regions.py --profile <aws-profile-name>
```

Replace <aws-profile-name> with the name of your AWS CLI profile (e.g., myorg-master).

---

## Example Usage
### Command:

```python
python us_all_enabled_regions.py --profile myorg-master
```

### Output:

```python
Found 35 SCPs. Processing...
Processing SCP ID: p-0lwt6gh9
Processing SCP ID: p-1a2b3c4d5e
Processing SCP ID: p-6f7g8h9i0j
Processing SCP ID: p-abcdef1234
Processing SCP ID: p-xyz9876543
.
.
.

Regions found in aws:RequestedRegion:
------------------
ap-east-1
ap-northeast-1
ap-southeast-1
ap-southeast-2
eu-west-2
me-central-1
me-south-1
us-east-1
us-east-2
us-west-1
us-west-2
------------------
```

---

## Notes

- **Error Handling**:
 - Ensure the AWS CLI profile you use has sufficient permissions to access SCPs in the organization.
 - If you encounter permission errors, verify that your IAM user or role has the required permissions.
- **Saving Output**:
 - To save the output to a file, redirect the script's output:

```python
python us_all_enabled_regions.py --profile myorg-master > regions_output.txt
```

- **Deactivating the Virtual Environment**:
 - Once you're done, deactivate the virtual environment:

## Additional Information
For more details about SCPs and AWS Organizations, refer to the [AWS Organizations Documentation.](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html)

If you encounter any issues or have feature requests, feel free to open an issue in the repository.
