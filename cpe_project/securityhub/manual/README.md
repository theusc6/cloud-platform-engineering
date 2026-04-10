
# Security Hub Manual Export Scripts

The main script is `export_security_hub_findings.py` which allows you to choose your export location, either local or S3. `local_export_security_hub_findings.py` is the original local-only version.

## Usage

Login with the correct AWS profile:

```bash
aws sso login --profile security-tooling
```

Check script options:

```bash
python3 export_security_hub_findings.py -h
usage: export_security_hub_findings.py [-h] -p PROFILE -e {local,s3} [-s {INFORMATIONAL,LOW,MEDIUM,HIGH,CRITICAL}]
```

Execute the script:

```bash
python3 export_security_hub_findings.py -p security-tooling -e s3
```

Sample output:

```
Exported findings to s3://myorg-security-hub-findings-exports/security_hub_findings_2023-03-02_16-42-50.xlsx
Elapsed time: 15.37 minutes
```

## Notes

The S3 export option will create a bucket if one doesn't exist, but the default configuration is minimal. For production use, create the bucket first using the `/infra/s3/s3_bucket_create.py` script to ensure proper encryption, versioning, and access controls are in place.
