# Deployments

Scripts that provision and deploy AWS infrastructure and integrations across accounts.

## Structure

| Directory/Script | Purpose |
|-----------------|---------|
| `inspector_deployer.py` | Deploy AWS Inspector across accounts |
| `terraform_deployment_prep.py` | Prepare accounts for Terraform-based deployments |
| `logging/` | Deploy centralized logging (CloudTrail, GuardDuty, Flow Logs, Resource Explorer) |
| `security_hub_exporter/` | Deploy automated Security Hub findings export infrastructure |
| `stitch/` | Deploy S3-based data integration with Stitch |

See `docs/` and subdirectory READMEs for detailed documentation.
