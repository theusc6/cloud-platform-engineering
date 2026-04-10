# Examples

Runnable workflows demonstrating how the CPE modules work together.

## S3 Compliance Workflow

**`s3_compliance_workflow.py`** — End-to-end check, report, and remediate cycle for an S3 bucket.

### Check only (read-only)

```bash
python3 -m examples.s3_compliance_workflow \
  -p my-sso-profile \
  -b my-bucket-name
```

### Check and auto-remediate

```bash
python3 -m examples.s3_compliance_workflow \
  -p my-sso-profile \
  -b my-bucket-name \
  --remediate
```

### Sample output

```
============================================================
  Compliance Report: S3 — my-bucket-name
============================================================
  [+] S3.4: Server-side encryption is enabled
  [!] S3.14: Versioning is not enabled
  [*] S3.14: Versioning enabled
  [+] S3.1/S3.8: Block public access is enabled
  [+] S3.9: Logging is enabled
  [+] Tags: Tags are present
──────────────────────────────────────────────────────────
  Summary: 4 PASS, 1 FAIL, 1 REMEDIATED
============================================================
```

### CI integration

The script exits with code 1 if any checks fail, making it usable as a CI gate:

```yaml
- name: S3 compliance check
  run: python3 -m examples.s3_compliance_workflow -p ci-profile -b $BUCKET
```
