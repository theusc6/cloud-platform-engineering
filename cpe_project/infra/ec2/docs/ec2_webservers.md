# AWS EC2 Instance Details Listing Script

This script enables the listing of details for all EC2 instances within the specified AWS account and regions. It leverages the AWS SDK for Python, Boto3, to access instance information and optionally writes the details to a CSV file.

**Author:** user

## Overview

This script offers an efficient way to retrieve and display EC2 instance details across multiple AWS regions. It requires the AWS profile name for Single Sign-On (SSO) login, and optionally, a CSV filename to which instance details can be written.

## How to Use

1. Replace the `AWS profile name for SSO login` and `Name of CSV file to write to` placeholders with the appropriate values in the script.

2. Run the script using a Python interpreter, ensuring you have the required dependencies installed.

## Script Execution

The script performs the following actions:

1. Parses command-line arguments to obtain the AWS profile name and CSV filename (if specified).

2. Initiates a Boto3 session using the provided AWS profile.

3. Iterates over a predefined list of AWS regions.

4. For each region, it:
   - Creates a Boto3 EC2 client specific to the region.
   - Retrieves a list of EC2 instances using the `describe_instances` API.
   - Extracts and displays details for each EC2 instance, including ID, type, state, and private IP address.
   - Optionally, appends the instance details to a CSV file if the filename is provided.

5. After processing all regions, if a CSV filename was provided, the script indicates where the instance details have been written.

## Note

- You need to have AWS CLI and Boto3 installed to run this script. Make sure you have the necessary permissions to access EC2 instances.
- If you choose to write the instance details to a CSV file, make sure you provide a valid and writable filename.
- The script offers a convenient way to get an overview of EC2 instances in different regions, making it particularly useful for managing instances across multiple geographic locations.
