# Architecture

This document describes the design decisions, module structure, and patterns used in the Cloud Platform Engineering repository.

## Design Philosophy

1. **Compliance as code** — Security checks and remediations are codified as Python classes, not manual runbooks. Every check is testable and repeatable.
2. **Separation of concerns** — Checking, reporting, and remediating are distinct operations. You can audit without changing anything, then opt in to remediation.
3. **Shared core, independent scripts** — Common patterns live in `cpe_project/core/`. Each script in `infra/` handles one service and runs standalone via CLI.
4. **Test without AWS** — All tests use mocked boto3 clients. No credentials, no cost, fast CI feedback.

## Module Architecture

```
cpe_project/
├── core/                  # Shared infrastructure — imported by all scripts
│   ├── aws_client.py      # Session management, retry config, error formatting
│   ├── compliance.py      # ComplianceCheck base class, result model
│   └── logger.py          # Structured logging (consistent format across scripts)
│
├── infra/                 # Service-specific compliance scripts
│   ├── s3/                # S3 compliance (check + remediate)
│   ├── ec2/               # EC2 security (IMDSv2, EBS encryption, SGs)
│   ├── rds/               # RDS hardening (deletion protection, IAM auth)
│   ├── kms/               # KMS key rotation
│   └── ...                # 15+ additional services
│
├── securityhub/           # Security Hub findings export
│   ├── manual/            # CLI-based export to XLSX
│   ├── lambda/            # Lambda function for scheduled exports
│   └── infra/             # CloudFormation deployer for the Lambda
│
├── deployments/           # Multi-account deployment scripts
├── queries/               # AWS resource inventory and reporting
└── policies/              # Service Control Policies
```

## Core Modules

### AWSClient (`core/aws_client.py`)

Wraps `boto3.Session` with:
- **Profile-based authentication** — all scripts use `--profile` for AWS SSO
- **Adaptive retry** — 3 retries with exponential backoff by default
- **Error formatting** — `handle_client_error()` extracts code and message from `ClientError`

```python
aws = AWSClient(profile="prod", region="us-east-1")
s3 = aws.client("s3")
```

### ComplianceCheck (`core/compliance.py`)

Base class implementing the **check → report → remediate** pipeline:

1. Subclasses register checks via `add_check(control_id, fn)` 
2. Optionally register fixes via `add_remediation(control_id, fn)`
3. `run()` executes all checks; `run(remediate=True)` also fixes failures
4. `print_report()` outputs a formatted summary

Each check returns a `ComplianceResult` with:
- `control` — AWS control ID (e.g., "S3.4")
- `status` — `PASS`, `FAIL`, `ERROR`, or `REMEDIATED`
- `resource` — the resource being checked
- `message` — human-readable description

### Logger (`core/logger.py`)

Provides consistent `[timestamp] [LEVEL] cpe.ModuleName — message` format across all scripts. Uses `stdout` so it works in terminals, CI, and CloudWatch Logs.

## Compliance Check Pattern

Every compliance script follows the same structure:

```python
class ServiceComplianceCheck(ComplianceCheck):
    def __init__(self, client, resource_id):
        super().__init__(resource_id=resource_id, service="ServiceName")
        self.add_check("CONTROL.1", self.check_something)
        self.add_remediation("CONTROL.1", self.fix_something)

    def check_something(self) -> ComplianceResult:
        # Returns PASS, FAIL, or ERROR

    def fix_something(self) -> ComplianceResult:
        # Returns REMEDIATED or ERROR
```

This pattern gives you:
- Consistent output format across all services
- Separation between auditing and remediation
- Easy testing (mock the client, call individual check methods)
- Composable: chain multiple compliance checks in a single workflow

## Multi-Account Strategy

Scripts authenticate via AWS SSO profiles (`--profile` flag). This supports the typical multi-account pattern:

```
Organization Root
├── Management Account      (profile: mgmt)
├── Security Account        (profile: security)
├── Shared Services         (profile: shared)
├── Dev Account             (profile: dev)
└── Prod Account            (profile: prod)
```

Run the same compliance script against different accounts:

```bash
# Check S3 compliance across environments
for profile in dev staging prod; do
    python3 -m cpe_project.infra.s3.s3_bucket_check -p $profile -b my-bucket
done
```

## CloudFormation Templates

Templates in `CloudFormation/` follow these conventions:
- **Parameterized** — no hardcoded resource names, account IDs, or regions
- **Security by default** — encryption enabled, public access blocked, logging configured
- **Tagged** — all resources include standard tags for cost allocation and ownership

## Testing Strategy

- **Unit tests** in `tests/` mirror the `cpe_project/` structure
- **Mocked boto3 clients** — tests never call AWS
- **Test both paths** — every check tests PASS, FAIL, and ERROR cases
- **Remediation tests** — verify the correct API calls are made and error handling works

Run the full suite:

```bash
pytest -v          # 49 tests, ~0.3s
```
