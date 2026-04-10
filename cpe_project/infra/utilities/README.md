# Infrastructure Utilities

Cross-service infrastructure scripts that don't belong to a single AWS service category.

| Script | Purpose |
|--------|---------|
| `aws_add_tags.py` | Add standard tags to AWS resources across services |
| `aws_create_pipeline_role.py` | Create IAM roles for CI/CD pipelines |
| `aws_ecs_readonly_root_comply.py` | Enforce read-only root filesystem on ECS containers (ECS.5) |
| `aws_fsx_create.py` | Create and configure AWS FSx file systems |

See `docs/` for detailed documentation on each script.
