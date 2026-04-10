#!/usr/bin/env python3

"""
Check S3 bucket compliance against AWS Foundational Security Best Practices v1.0.0.

https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html

Controls checked:
  [S3.1]  S3 Block Public Access setting should be enabled
  [S3.4]  S3 buckets should have server-side encryption enabled
  [S3.8]  S3 Block Public Access setting should be enabled at the bucket-level
  [S3.9]  S3 bucket server access logging should be enabled
  [S3.14] S3 buckets should use versioning
"""

import argparse
import sys

from botocore.exceptions import ClientError

from cpe_project.core.aws_client import AWSClient
from cpe_project.core.compliance import ComplianceCheck, ComplianceResult, Status
from cpe_project.core.logger import get_logger

log = get_logger("S3BucketCheck")


class S3BucketComplianceCheck(ComplianceCheck):
    """Compliance checks for a single S3 bucket."""

    def __init__(self, s3_client, bucket_name: str):
        super().__init__(resource_id=bucket_name, service="S3")
        self.s3 = s3_client
        self.bucket = bucket_name

        self.add_check("S3.4", self.check_encryption)
        self.add_check("S3.14", self.check_versioning)
        self.add_check("S3.1/S3.8", self.check_public_access_block)
        self.add_check("S3.9", self.check_logging)
        self.add_check("Tags", self.check_tags)

    def check_encryption(self) -> ComplianceResult:
        try:
            self.s3.get_bucket_encryption(Bucket=self.bucket)
            return ComplianceResult(
                control="S3.4", status=Status.PASS,
                resource=self.bucket,
                message="Server-side encryption is enabled",
            )
        except ClientError:
            return ComplianceResult(
                control="S3.4", status=Status.FAIL,
                resource=self.bucket,
                message="Server-side encryption is not enabled",
            )

    def check_versioning(self) -> ComplianceResult:
        try:
            resp = self.s3.get_bucket_versioning(Bucket=self.bucket)
            if resp.get("Status") == "Enabled":
                return ComplianceResult(
                    control="S3.14", status=Status.PASS,
                    resource=self.bucket,
                    message="Bucket versioning is Enabled",
                )
            return ComplianceResult(
                control="S3.14", status=Status.FAIL,
                resource=self.bucket,
                message="Bucket versioning is not enabled",
            )
        except ClientError as e:
            return ComplianceResult(
                control="S3.14", status=Status.ERROR,
                resource=self.bucket,
                message=AWSClient.handle_client_error(e, "versioning check"),
            )

    def check_public_access_block(self) -> ComplianceResult:
        try:
            self.s3.get_public_access_block(Bucket=self.bucket)
            return ComplianceResult(
                control="S3.1/S3.8", status=Status.PASS,
                resource=self.bucket,
                message="Block public access is enabled",
            )
        except ClientError as e:
            code = e.response["Error"]["Code"]
            if code == "NoSuchPublicAccessBlockConfiguration":
                return ComplianceResult(
                    control="S3.1/S3.8", status=Status.FAIL,
                    resource=self.bucket,
                    message="Block public access is not enabled",
                )
            return ComplianceResult(
                control="S3.1/S3.8", status=Status.ERROR,
                resource=self.bucket,
                message=AWSClient.handle_client_error(e, "public access check"),
            )

    def check_logging(self) -> ComplianceResult:
        try:
            resp = self.s3.get_bucket_logging(Bucket=self.bucket)
            if "LoggingEnabled" in resp:
                return ComplianceResult(
                    control="S3.9", status=Status.PASS,
                    resource=self.bucket,
                    message="Bucket logging is enabled",
                )
            return ComplianceResult(
                control="S3.9", status=Status.FAIL,
                resource=self.bucket,
                message="Bucket logging is not enabled",
            )
        except ClientError as e:
            return ComplianceResult(
                control="S3.9", status=Status.ERROR,
                resource=self.bucket,
                message=AWSClient.handle_client_error(e, "logging check"),
            )

    def check_tags(self) -> ComplianceResult:
        try:
            self.s3.get_bucket_tagging(Bucket=self.bucket)
            return ComplianceResult(
                control="Tags", status=Status.PASS,
                resource=self.bucket,
                message="Tags are present",
            )
        except ClientError as e:
            code = e.response["Error"]["Code"]
            if code == "NoSuchTagSet":
                return ComplianceResult(
                    control="Tags", status=Status.FAIL,
                    resource=self.bucket,
                    message="No tags are set",
                )
            return ComplianceResult(
                control="Tags", status=Status.ERROR,
                resource=self.bucket,
                message=AWSClient.handle_client_error(e, "tag check"),
            )


def main():
    parser = argparse.ArgumentParser(
        description="Check S3 bucket compliance with AWS Foundational Security Best Practices v1"
    )
    parser.add_argument("-b", "--bucket", required=True, help="S3 bucket name")
    parser.add_argument("-p", "--profile", required=True, help="AWS profile name")
    parser.add_argument("-r", "--region", default="us-east-1", help="AWS region")
    args = parser.parse_args()

    aws = AWSClient(profile=args.profile, region=args.region)
    s3_client = aws.client("s3")

    try:
        s3_client.head_bucket(Bucket=args.bucket)
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "404":
            log.error("Bucket '%s' does not exist.", args.bucket)
        elif code == "403":
            log.error("Access denied to bucket '%s'.", args.bucket)
        else:
            log.error("Error accessing bucket: %s", AWSClient.handle_client_error(e))
        sys.exit(1)

    checker = S3BucketComplianceCheck(s3_client, args.bucket)
    checker.run()
    checker.print_report()


if __name__ == "__main__":
    main()
