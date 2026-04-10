
# Cloud Platform Engineering

![Sonarcloud status](https://github.com/theusc6/cloud-platform-engineering/actions/workflows/build.yaml/badge.svg?event=push)  ![Python status](https://github.com/theusc6/cloud-platform-engineering/actions/workflows/pylint.yaml/badge.svg?event=push)

**Automated AWS security compliance and infrastructure management at scale.**

---

## The Problem

Managing security compliance across multiple AWS accounts is a manual, error-prone process. Security Hub generates hundreds of findings, each requiring investigation and remediation. Teams spend hours clicking through consoles, fixing one resource at a time, only to fall behind as new findings appear.

## The Solution

This repository provides a Python-based automation framework that:

1. **Scans** AWS resources against [AWS Foundational Security Best Practices](https://docs.aws.amazon.com/securityhub/latest/userguide/fsbp-standard.html) and generates compliance reports
2. **Remediates** non-compliant resources automatically — encryption, versioning, public access blocking, logging, and more
3. **Deploys** security tooling (Inspector, Config rules, flow logs) across accounts via Infrastructure-as-Code
4. **Exports** Security Hub findings for offline analysis and executive reporting

Built on a reusable `core` module that provides shared AWS session management, a compliance check/remediation framework, and structured logging — so every script follows the same pattern and produces consistent output.

## Architecture

```
                    ┌─────────────────────────────┐
                    │      CLI (argparse)          │
                    └──────────┬──────────────────┘
                               │
                    ┌──────────▼──────────────────┐
                    │   cpe_project/core/          │
                    │  ┌───────────────────────┐   │
                    │  │ AWSClient             │   │  Session management, retry, error handling
                    │  │ ComplianceCheck       │   │  Check → Report → Remediate pipeline
                    │  │ Logger                │   │  Structured logging
                    │  └───────────────────────┘   │
                    └──────────┬──────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                     │
  ┌───────▼────────┐  ┌───────▼────────┐  ┌────────▼───────┐
  │  infra/         │  │  securityhub/  │  │  deployments/  │
  │  S3, EC2, RDS,  │  │  Findings      │  │  Inspector,    │
  │  KMS, VPC ...   │  │  export/report │  │  Logging, ...  │
  └────────────────┘  └────────────────┘  └────────────────┘
          │
    ┌─────┴──────┐
    │ CloudFormation/ │  IaC templates (CloudWatch, Backup, Nuke)
    └────────────────┘
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for design decisions and multi-account strategy.

## Quick Start

```bash
# Clone and set up
git clone https://github.com/theusc6/cloud-platform-engineering.git
cd cloud-platform-engineering
python3 -m venv .venv
source .venv/bin/activate
pip install -r cpe_project/requirements.txt

# Authenticate with AWS SSO
aws sso login --profile <your-profile>

# Check S3 bucket compliance
python3 -m cpe_project.infra.s3.s3_bucket_check -p <profile> -b <bucket-name>

# Auto-remediate a non-compliant bucket
python3 -m cpe_project.infra.s3.s3_make_bucket_comply -p <profile> -b <bucket-name>

# Run tests
pip install pytest
pytest
```

## Project Layout

```
cloud-platform-engineering/
├── cpe_project/
│   ├── core/               # Shared modules (AWSClient, ComplianceCheck, Logger)
│   ├── infra/              # Service-specific compliance scripts
│   │   ├── s3/             #   S3 encryption, versioning, public access, logging
│   │   ├── ec2/            #   IMDSv2, EBS encryption, security groups
│   │   ├── rds/            #   Deletion protection, IAM auth, monitoring
│   │   ├── kms/            #   Key rotation
│   │   ├── ecr/            #   Image scanning, lifecycle policies
│   │   ├── vpc/            #   Flow logs, default SG compliance
│   │   └── ...             #   ELB, CloudFront, WAF, DynamoDB, SQS, etc.
│   ├── securityhub/        # Security Hub findings export (CLI, Lambda, infra)
│   ├── deployments/        # Multi-account deployment scripts
│   ├── queries/            # AWS resource inventory and reporting
│   └── policies/           # Service Control Policies (SCPs)
├── CloudFormation/         # IaC templates (CloudWatch, Backup, S3, Nuke)
├── examples/               # End-to-end runnable workflows
├── tests/                  # pytest suite (49 tests)
└── docs/                   # Architecture and design documentation
```

## Key Capabilities

### Compliance Checking & Remediation

Every compliance script follows the same pattern using the `ComplianceCheck` base class:

```python
from cpe_project.core import AWSClient, ComplianceCheck, ComplianceResult, Status

class S3BucketComplianceCheck(ComplianceCheck):
    def __init__(self, s3_client, bucket_name):
        super().__init__(resource_id=bucket_name, service="S3")
        self.add_check("S3.4", self.check_encryption)
        self.add_remediation("S3.4", self.fix_encryption)
```

Run checks, get a formatted report, optionally auto-remediate:

```
============================================================
  Compliance Report: S3 — my-bucket
============================================================
  [+] S3.4: Server-side encryption is enabled
  [!] S3.14: Versioning is not enabled
  [+] S3.1/S3.8: Block public access is enabled
  [!] S3.9: Logging is not enabled
  [+] Tags: Tags are present
──────────────────────────────────────────────────────────
  Summary: 3 PASS, 2 FAIL
============================================================
```

### Services Covered

| Service | Controls | Script Count |
|---------|----------|-------------|
| S3 | Encryption, versioning, public access, logging, SSL | 9 |
| EC2 | IMDSv2, EBS encryption, security groups, default VPC | 7 |
| RDS | Deletion protection, IAM auth, monitoring, logging | 7 |
| VPC | Flow logs, default SG, S2S VPN logging | 3 |
| ECR | Image scanning, lifecycle policies, tag immutability | 3 |
| KMS, ELB, DynamoDB, SQS, CloudFront, WAF, etc. | Various | 10+ |

### Infrastructure as Code

CloudFormation templates for CloudWatch dashboards, AWS Backup policies, S3 bucket provisioning, and AWS Nuke account cleanup — all parameterized and documented.

## Testing

```bash
pytest -v                    # Run all 49 tests
pytest tests/core/           # Core module tests only
pytest tests/infra/s3/       # S3 compliance tests only
```

Tests use mocked boto3 clients — no AWS credentials required.

## Contributing

Contributions welcome. See [CONTRIBUTING.md](cpe_project/CONTRIBUTING.md) for guidelines.

## License

MIT License. See [LICENSE](LICENSE) for details.
