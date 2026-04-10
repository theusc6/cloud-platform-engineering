#!/usr/bin/env python3

"""
Remediate S3 bucket compliance against AWS Foundational Security Best Practices v1.0.0.

https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html

Controls enforced:
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

log = get_logger("S3MakeBucketComply")


class S3BucketRemediation(ComplianceCheck):
    """Check and remediate S3 bucket compliance in a single pass."""

    def __init__(self, s3_client, bucket_name: str):
        super().__init__(resource_id=bucket_name, service="S3")
        self.s3 = s3_client
        self.bucket = bucket_name

        self.add_check("S3.4", self.check_encryption)
        self.add_check("S3.14", self.check_versioning)
        self.add_check("S3.1/S3.8", self.check_public_access_block)
        self.add_check("S3.9", self.check_logging)
        self.add_check("Tags", self.check_tags)

        self.add_remediation("S3.4", self.fix_encryption)
        self.add_remediation("S3.14", self.fix_versioning)
        self.add_remediation("S3.1/S3.8", self.fix_public_access_block)
        self.add_remediation("S3.9", self.fix_logging)
        self.add_remediation("Tags", self.fix_tags)

    def check_encryption(self) -> ComplianceResult:
        try:
            self.s3.get_bucket_encryption(Bucket=self.bucket)
            return ComplianceResult(control="S3.4", status=Status.PASS, resource=self.bucket, message="Server-side encryption is enabled")
        except ClientError:
            return ComplianceResult(control="S3.4", status=Status.FAIL, resource=self.bucket, message="Server-side encryption is not enabled")

    def check_versioning(self) -> ComplianceResult:
        try:
            resp = self.s3.get_bucket_versioning(Bucket=self.bucket)
            if resp.get("Status") == "Enabled":
                return ComplianceResult(control="S3.14", status=Status.PASS, resource=self.bucket, message="Versioning is enabled")
            return ComplianceResult(control="S3.14", status=Status.FAIL, resource=self.bucket, message="Versioning is not enabled")
        except ClientError as e:
            return ComplianceResult(control="S3.14", status=Status.ERROR, resource=self.bucket, message=AWSClient.handle_client_error(e))

    def check_public_access_block(self) -> ComplianceResult:
        try:
            self.s3.get_public_access_block(Bucket=self.bucket)
            return ComplianceResult(control="S3.1/S3.8", status=Status.PASS, resource=self.bucket, message="Block public access is enabled")
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchPublicAccessBlockConfiguration":
                return ComplianceResult(control="S3.1/S3.8", status=Status.FAIL, resource=self.bucket, message="Block public access is not enabled")
            return ComplianceResult(control="S3.1/S3.8", status=Status.ERROR, resource=self.bucket, message=AWSClient.handle_client_error(e))

    def check_logging(self) -> ComplianceResult:
        try:
            resp = self.s3.get_bucket_logging(Bucket=self.bucket)
            if "LoggingEnabled" in resp:
                return ComplianceResult(control="S3.9", status=Status.PASS, resource=self.bucket, message="Logging is enabled")
            return ComplianceResult(control="S3.9", status=Status.FAIL, resource=self.bucket, message="Logging is not enabled")
        except ClientError as e:
            return ComplianceResult(control="S3.9", status=Status.ERROR, resource=self.bucket, message=AWSClient.handle_client_error(e))

    def check_tags(self) -> ComplianceResult:
        try:
            self.s3.get_bucket_tagging(Bucket=self.bucket)
            return ComplianceResult(control="Tags", status=Status.PASS, resource=self.bucket, message="Tags are present")
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchTagSet":
                return ComplianceResult(control="Tags", status=Status.FAIL, resource=self.bucket, message="No tags are set")
            return ComplianceResult(control="Tags", status=Status.ERROR, resource=self.bucket, message=AWSClient.handle_client_error(e))

    def fix_encryption(self) -> ComplianceResult:
        try:
            self.s3.put_bucket_encryption(Bucket=self.bucket, ServerSideEncryptionConfiguration={"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]})
            return ComplianceResult(control="S3.4", status=Status.REMEDIATED, resource=self.bucket, message="Server-side encryption enabled")
        except ClientError as e:
            return ComplianceResult(control="S3.4", status=Status.ERROR, resource=self.bucket, message=f"Failed to enable encryption: {AWSClient.handle_client_error(e)}")

    def fix_versioning(self) -> ComplianceResult:
        try:
            self.s3.put_bucket_versioning(Bucket=self.bucket, VersioningConfiguration={"Status": "Enabled"})
            return ComplianceResult(control="S3.14", status=Status.REMEDIATED, resource=self.bucket, message="Versioning enabled")
        except ClientError as e:
            return ComplianceResult(control="S3.14", status=Status.ERROR, resource=self.bucket, message=f"Failed to enable versioning: {AWSClient.handle_client_error(e)}")

    def fix_public_access_block(self) -> ComplianceResult:
        try:
            self.s3.put_public_access_block(Bucket=self.bucket, PublicAccessBlockConfiguration={"BlockPublicAcls": True, "IgnorePublicAcls": True, "BlockPublicPolicy": True, "RestrictPublicBuckets": True})
            return ComplianceResult(control="S3.1/S3.8", status=Status.REMEDIATED, resource=self.bucket, message="Block public access enabled")
        except ClientError as e:
            return ComplianceResult(control="S3.1/S3.8", status=Status.ERROR, resource=self.bucket, message=f"Failed to block public access: {AWSClient.handle_client_error(e)}")

    def fix_logging(self) -> ComplianceResult:
        try:
            self.s3.put_bucket_logging(Bucket=self.bucket, BucketLoggingStatus={"LoggingEnabled": {"TargetBucket": self.bucket, "TargetPrefix": "logs/"}})
            return ComplianceResult(control="S3.9", status=Status.REMEDIATED, resource=self.bucket, message="Logging enabled")
        except ClientError as e:
            return ComplianceResult(control="S3.9", status=Status.ERROR, resource=self.bucket, message=f"Failed to enable logging: {AWSClient.handle_client_error(e)}")

    def fix_tags(self) -> ComplianceResult:
        try:
            self.s3.put_bucket_tagging(Bucket=self.bucket, Tagging={"TagSet": [{"Key": "Category", "Value": "DevOps"}, {"Key": "Product", "Value": "S3 Bucket"}]})
            return ComplianceResult(control="Tags", status=Status.REMEDIATED, resource=self.bucket, message="Default tags applied")
        except ClientError as e:
            return ComplianceResult(control="Tags", status=Status.ERROR, resource=self.bucket, message=f"Failed to set tags: {AWSClient.handle_client_error(e)}")


def main():
    parser = argparse.ArgumentParser(description="Remediate S3 bucket compliance with AWS Foundational Security Best Practices v1")
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
            log.error("Error: %s", AWSClient.handle_client_error(e))
        sys.exit(1)

    remediation = S3BucketRemediation(s3_client, args.bucket)
    remediation.run(remediate=True)
    remediation.print_report()


if __name__ == "__main__":
    main()
