# Python for SecurityHub Reporting

## How to navigate this repository

- `exports` - contains the *.xlsx findings reports from SecurityHub
- `infra`   - contains the required infrastructure, in this case an S3 bucket and folder
- `lambda`  - the AWS Lambda function for generating the SecurityHub findings report
- `manual`  - the manual script that can be executed locally to do the same thing the lambda function is doing
- `old`     - old iterations of files that are no longer being used, arguably can be deleted
- `report-remediation` - scripts to fix SecurityHub findings
- `tests`   - tests for python scripts in Sonarcloud

---

## How to use this repository

This repository is primarily designed to maintain the lambda function that is being used to automatically generate the SecurityHub findings report in an S3 bucket.  It also houses the manual scripts should they be required to run the export locally as well as some other "python" aspects related to SecurityHub.

Everything in this repository resides in the AWS `security-tooling` account, which is where the SeucityHub service is running and configured.

The `/infra/s3-create-bucket.py` script will create the required AWS S3 bucket that the lambda function will export the SeucityHub findings report into.

---

## References

- [Create a CloudWatch Event Rule](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/Create-CloudWatch-Events-Rule.html)

---

## What's in this repository

```bash
.
├── .coverage
├── README.md
├── exports
│   └── security_hub_findings_2023-02-21_12-38-57.xlsx
├── infra
│   └── s3-create-bucket.py
├── lambda
│   ├── README.md
│   └── lambda-export-secuty-hub-findings.py
├── manual
│   └── export-security-hub-findings.py
├── old
│   └── export_security_hub_findings.py
├── report-remediation
│   ├── s3-bucket-version-enable.py
│   ├── s3-deny-public.py
│   └── s3-enable-ss-encrypt.py
├── requirements.txt
├── test_export_security_hub_findings.py
└── tests
    └── s3-bucket-version-enable-test.py

8 directories, 14 files
```

---
