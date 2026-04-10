import boto3
from botocore.config import Config

# AWS session configuration
session = boto3.Session(profile_name="don_sso_prod_security-tooling", region_name="us-west-2")

# Spoof CLI User-Agent
cfg = Config(user_agent_extra="aws-cli/2.31.14 exec-env/CLI compat")

# Initialize Resource Explorer client
rx = session.client("resource-explorer-2", config=cfg)

# Production accounts
PROD_ACCOUNTS = [
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  # account-name-service-prod
    "123456789012",  
    "123456789012",  # account-name-service-prod
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  # Log Archive
    "123456789012",  # Security Tooling
    "123456789012",  
    "123456789012",  
    "123456789012",  # Audit
    "123456789012",  # devops
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
]

# Development accounts
DEV_ACCOUNTS = [
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
]

# UAT accounts
UAT_ACCOUNTS = [
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  
    "123456789012",  # account-name-service-shared
    "123456789012",  # account-name-service-stage
    "123456789012",  
]

TEST = [
    "123456789012",  
    "123456789012",  
]

# Create the FilterString by joining account IDs with commas
filter_string = f"accountid:{','.join(account_ids)}"

try:
    resp = rx.create_view(
        ViewName="ua-spoof-test2",
        Filters={"FilterString": filter_string},
        IncludedProperties=[{"Name": "tags"}],
        Scope="arn:aws:organizations::123456789012:organization/o-3jj2faa76f"
    )
    print("✅ Created:", resp["View"]["ViewArn"])
except Exception as e:
    print("❌ Failed:", e)