#!/usr/bin/env python3

"""
End-to-end S3 compliance workflow.

This example demonstrates the full check → report → remediate cycle
for an S3 bucket using the CPE core modules.

Usage:
    # Check only (read-only, safe to run anytime)
    python3 -m examples.s3_compliance_workflow -p <profile> -b <bucket>

    # Check and auto-remediate non-compliant settings
    python3 -m examples.s3_compliance_workflow -p <profile> -b <bucket> --remediate
"""

import argparse
import sys

from botocore.exceptions import ClientError

from cpe_project.core.aws_client import AWSClient
from cpe_project.core.compliance import Status
from cpe_project.core.logger import get_logger
from cpe_project.infra.s3.s3_bucket_check import S3BucketComplianceCheck
from cpe_project.infra.s3.s3_make_bucket_comply import S3BucketRemediation

log = get_logger("S3Workflow")


def main():
    parser = argparse.ArgumentParser(
        description="End-to-end S3 compliance workflow: check, report, remediate"
    )
    parser.add_argument("-p", "--profile", required=True, help="AWS profile name")
    parser.add_argument("-b", "--bucket", required=True, help="S3 bucket name")
    parser.add_argument("-r", "--region", default="us-east-1", help="AWS region")
    parser.add_argument(
        "--remediate", action="store_true",
        help="Automatically fix non-compliant settings",
    )
    args = parser.parse_args()

    # ── Step 1: Connect ─────────────────────────────────────
    aws = AWSClient(profile=args.profile, region=args.region)
    s3 = aws.client("s3")

    # Verify the bucket exists
    try:
        s3.head_bucket(Bucket=args.bucket)
        log.info("Bucket '%s' exists and is accessible.", args.bucket)
    except ClientError as e:
        log.error("Cannot access bucket: %s", AWSClient.handle_client_error(e))
        sys.exit(1)

    # ── Step 2: Check compliance ────────────────────────────
    if args.remediate:
        log.info("Running compliance checks with auto-remediation...")
        workflow = S3BucketRemediation(s3, args.bucket)
        workflow.run(remediate=True)
    else:
        log.info("Running compliance checks (read-only)...")
        workflow = S3BucketComplianceCheck(s3, args.bucket)
        workflow.run()

    # ── Step 3: Report ──────────────────────────────────────
    workflow.print_report()

    # Exit with non-zero if any checks failed (useful in CI)
    summary = workflow.summary()
    if summary.get("FAIL", 0) > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
