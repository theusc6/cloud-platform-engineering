# Delete AWS CloudTrail Script

This script provides functionality to delete a specific AWS CloudTrail trail.

## Requirements

- Python 3
- `boto3` library
- AWS credentials set up to allow deletion of CloudTrail trails

## Usage

Run the script using the following command:

\`\`\`bash
python3 delete_cloudtrail.py --profile <profile_name> --trail <trail_name>
\`\`\`

### Arguments

- `--profile` (`-p`): Specifies the AWS profile name for SSO login. Required.
- `--trail` (`-t`): Specifies the CloudTrail trail name you want to delete. Required.
- `--region` (`-r`): AWS region for the trail. Required.

## Script Details

1. **Argument Parsing**: The script starts by parsing the necessary command-line arguments (profile name and trail name).

2. **Deleting CloudTrail**: The main functionality involves using the `boto3` library to delete the specified CloudTrail trail. It handles multiple types of exceptions that may occur, such as:

    - `TrailNotFoundException`: Indicates that the trail cannot be found.
    - `InvalidTrailNameException`: Indicates that the entered trail name is invalid.
    - `InvalidHomeRegionException`: Indicates that an invalid region has been entered.
    - `UnsupportedOperationException`: Indicates that the operation is not supported.

## Examples

To delete a CloudTrail trail named `MyTrail`, in the `us-west-2` region, using the AWS profile `myprofile`, you'd run:

\`\`\`bash
python3 delete_cloudtrail.py --profile myprofile --trail MyTrail --region us-west-2
\`\`\`
