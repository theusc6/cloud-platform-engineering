# Create AWS FSx File System and Share

This script automates the creation of an Amazon Web Services (AWS) FSx file system and shares it with a specified CIDR block. The script is designed to simplify the process of setting up and configuring the FSx file system, ensuring secure access within the designated network.

## Overview

The purpose of this script is to streamline the process of creating an AWS FSx file system, configuring its security group, and setting up access for a specific CIDR block. By utilizing the Boto3 library, the script ensures that the creation process is accurate, secure, and efficient.

## How to Use

1. Replace the placeholders in the script with appropriate values for your AWS environment.
   - `VPC ID`: The ID of the Virtual Private Cloud (VPC) where the FSx file system will be created.
   - `Subnet ID`: The ID of the subnet where the FSx file system will be created.
   - `Allowed CIDR`: The CIDR block that is allowed to access the FSx file system.
   - `Profile`: The name of the AWS profile for authentication.

2. Run the script using a Python interpreter with the required dependencies installed.

## Script Execution

The script performs the following actions:

1. Validates the provided CIDR block.

2. Establishes an AWS session using the provided profile.

3. Creates a security group for the FSx file system.

4. Configures inbound traffic rules to allow access from the specified CIDR block to the security group.

5. Creates the AWS FSx file system with the defined specifications.

6. Waits for the file system to be available.

7. Creates an SMB file share associated with the file system, configured for Active Directory authentication.

8. Prints relevant information about the created file share.

## Note

- This script simplifies the process of creating and sharing an AWS FSx file system while adhering to security best practices.
- The script enhances automation by leveraging the Boto3 library to interact with AWS services.
- Ensure that the provided CIDR block is valid and accurate to prevent unauthorized access.

---

By using this script, you can effortlessly create and share an AWS FSx file system, ensuring that it is properly secured and accessible to the specified CIDR block. This contributes to smoother workflows and consistent security practices within your AWS infrastructure.
