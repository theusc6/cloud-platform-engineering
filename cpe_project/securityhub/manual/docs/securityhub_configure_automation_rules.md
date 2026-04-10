# SecurityHub Automation Rules
This module defines rules for AWS SecurityHub and includes functions to create automation rules. These automation rules allow for the suppression of findings and other automated actions based on specified criteria.

## How to Use
To utilize this script, you must provide the appropriate AWS profile and region as command-line arguments. The rules defined in the rules list will be created in the specified AWS account and region.

## Prerequisites
- Python 3.x
- Boto3 library installed
- Properly configured AWS credentials

## Command-Line Arguments
--profile: (Required) AWS SSO profile name
--region: (Optional) AWS region (default: us-west-2)

### Example Usage
`python securityhub_configure_automation_rules.py --profile <profile-name> --region <region>`

### Defined Rules
The rules defined within this script include various conditions and actions, such as:

- Finding suppression for specific resource criteria
- Enabling or disabling specific rules based on existing settings
- Error handling for common exceptions

Each rule has specific attributes, including:

  - RuleStatus: The status of the rule (ENABLED/DISABLED)
  - RuleOrder: The order of the rule
  - RuleName: The name of the rule
  - Description: A description of the rule
  - IsTerminal: Boolean value determining if the rule is terminal
  - Criteria: The criteria used to match findings
  - Actions: The actions to take if the criteria are met

### Functions
`get_existing_rules(session)`
Retrieves existing automation rules from SecurityHub. It's used to prevent duplicate rules.

`create_automation_rules(session)`
Loops through the rules and applies them to SecurityHub in the management account and region.

`main()`
The main function for taking arguments, building the session, and running the script.

### Additional Information
As new rules need to be added, simply add them within the 'rules' list. Ensure the rules are crafted following the AWS SecurityHub documentation to avoid errors or unexpected behaviors.
