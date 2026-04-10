# S3 - Stitch Integration Script

## Overview

This script facilitates the automated creation and management of IAM policies and roles in AWS, specifically for S3 & Stitch integration. It allows the creation of a new IAM policy and role, attaching specific permissions and tags, and subsequently linking the policy to the role.

## Actions

The script performs the following actions:

Creates an IAM policy with specified permissions for S3 bucket access.
Creates an IAM role with a trust policy for Stitch integration.
Attaches the created IAM policy to the newly created IAM role.
Applies tags to the IAM role for easier management and tracking.

## Usage

` python s3_stitch_integration.py 
    --profile <profile_name> 
    --bucket_name <bucket_name>
    --stitch_account_id <stitch_account_id> 
    --stitch_external_id <stitch_external_id>
    --environment <environment> 
    --owner <owner> 
    --ticket_number <ticket_number>
    --role_name <role_name>`

## Target(s)

This script is intended for use in AWS accounts requiring automated setup of IAM roles and policies for S3 and Stitch integration, especially in multi-environment setups.

## Considerations

- Before the script can be ran, all information must be provided by requestor in ticket.
- The script introduces delays after creating the policy and role to account for AWS propagation times.
- Review and modify the permissions in the policy document according to your specific S3 access requirements.
- The role's trust policy should be aligned with your Stitch account's requirements. 
- Tags are customizable based on the need for resource tracking and management. The only two tags required are "Owner" & "Ticket Number".
