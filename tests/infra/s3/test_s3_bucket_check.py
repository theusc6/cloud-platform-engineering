"""Tests for S3 bucket compliance checks.

Tests the S3BucketComplianceCheck class against mocked boto3 S3 clients
to validate compliance check logic without AWS credentials.
"""

from unittest.mock import MagicMock
from botocore.exceptions import ClientError
import pytest

from cpe_project.core.compliance import Status
from cpe_project.infra.s3.s3_bucket_check import S3BucketComplianceCheck


def make_client_error(code, message="error"):
    return ClientError(
        {"Error": {"Code": code, "Message": message}}, "operation"
    )


@pytest.fixture
def s3_client():
    return MagicMock()


class TestCheckEncryption:
    def test_pass_when_encrypted(self, s3_client):
        s3_client.get_bucket_encryption.return_value = {
            "ServerSideEncryptionConfiguration": {
                "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]
            }
        }
        checker = S3BucketComplianceCheck(s3_client, "my-bucket")
        result = checker.check_encryption()
        assert result.status == Status.PASS

    def test_fail_when_not_encrypted(self, s3_client):
        s3_client.get_bucket_encryption.side_effect = make_client_error(
            "ServerSideEncryptionConfigurationNotFoundError"
        )
        checker = S3BucketComplianceCheck(s3_client, "my-bucket")
        result = checker.check_encryption()
        assert result.status == Status.FAIL


class TestCheckVersioning:
    def test_pass_when_enabled(self, s3_client):
        s3_client.get_bucket_versioning.return_value = {"Status": "Enabled"}
        checker = S3BucketComplianceCheck(s3_client, "my-bucket")
        result = checker.check_versioning()
        assert result.status == Status.PASS

    def test_fail_when_suspended(self, s3_client):
        s3_client.get_bucket_versioning.return_value = {"Status": "Suspended"}
        checker = S3BucketComplianceCheck(s3_client, "my-bucket")
        result = checker.check_versioning()
        assert result.status == Status.FAIL

    def test_fail_when_not_configured(self, s3_client):
        s3_client.get_bucket_versioning.return_value = {}
        checker = S3BucketComplianceCheck(s3_client, "my-bucket")
        result = checker.check_versioning()
        assert result.status == Status.FAIL

    def test_error_on_client_error(self, s3_client):
        s3_client.get_bucket_versioning.side_effect = make_client_error("InternalError")
        checker = S3BucketComplianceCheck(s3_client, "my-bucket")
        result = checker.check_versioning()
        assert result.status == Status.ERROR


class TestCheckPublicAccessBlock:
    def test_pass_when_blocked(self, s3_client):
        s3_client.get_public_access_block.return_value = {
            "PublicAccessBlockConfiguration": {
                "BlockPublicAcls": True, "IgnorePublicAcls": True,
                "BlockPublicPolicy": True, "RestrictPublicBuckets": True,
            }
        }
        checker = S3BucketComplianceCheck(s3_client, "my-bucket")
        result = checker.check_public_access_block()
        assert result.status == Status.PASS

    def test_fail_when_no_config(self, s3_client):
        s3_client.get_public_access_block.side_effect = make_client_error(
            "NoSuchPublicAccessBlockConfiguration"
        )
        checker = S3BucketComplianceCheck(s3_client, "my-bucket")
        result = checker.check_public_access_block()
        assert result.status == Status.FAIL

    def test_error_on_other_error(self, s3_client):
        s3_client.get_public_access_block.side_effect = make_client_error("AccessDenied")
        checker = S3BucketComplianceCheck(s3_client, "my-bucket")
        result = checker.check_public_access_block()
        assert result.status == Status.ERROR


class TestCheckLogging:
    def test_pass_when_enabled(self, s3_client):
        s3_client.get_bucket_logging.return_value = {
            "LoggingEnabled": {"TargetBucket": "log-bucket", "TargetPrefix": "logs/"}
        }
        checker = S3BucketComplianceCheck(s3_client, "my-bucket")
        result = checker.check_logging()
        assert result.status == Status.PASS

    def test_fail_when_disabled(self, s3_client):
        s3_client.get_bucket_logging.return_value = {}
        checker = S3BucketComplianceCheck(s3_client, "my-bucket")
        result = checker.check_logging()
        assert result.status == Status.FAIL

    def test_error_on_client_error(self, s3_client):
        s3_client.get_bucket_logging.side_effect = make_client_error("InternalError")
        checker = S3BucketComplianceCheck(s3_client, "my-bucket")
        result = checker.check_logging()
        assert result.status == Status.ERROR


class TestCheckTags:
    def test_pass_when_tagged(self, s3_client):
        s3_client.get_bucket_tagging.return_value = {
            "TagSet": [{"Key": "Env", "Value": "prod"}]
        }
        checker = S3BucketComplianceCheck(s3_client, "my-bucket")
        result = checker.check_tags()
        assert result.status == Status.PASS

    def test_fail_when_no_tags(self, s3_client):
        s3_client.get_bucket_tagging.side_effect = make_client_error("NoSuchTagSet")
        checker = S3BucketComplianceCheck(s3_client, "my-bucket")
        result = checker.check_tags()
        assert result.status == Status.FAIL

    def test_error_on_other_error(self, s3_client):
        s3_client.get_bucket_tagging.side_effect = make_client_error("AccessDenied")
        checker = S3BucketComplianceCheck(s3_client, "my-bucket")
        result = checker.check_tags()
        assert result.status == Status.ERROR


class TestFullComplianceRun:
    def test_all_passing(self, s3_client):
        s3_client.get_bucket_encryption.return_value = {"ServerSideEncryptionConfiguration": {}}
        s3_client.get_bucket_versioning.return_value = {"Status": "Enabled"}
        s3_client.get_public_access_block.return_value = {"PublicAccessBlockConfiguration": {}}
        s3_client.get_bucket_logging.return_value = {"LoggingEnabled": {}}
        s3_client.get_bucket_tagging.return_value = {"TagSet": []}

        checker = S3BucketComplianceCheck(s3_client, "compliant-bucket")
        results = checker.run()

        assert len(results) == 5
        assert all(r.status == Status.PASS for r in results)
        assert checker.summary() == {"PASS": 5}

    def test_mixed_results(self, s3_client):
        s3_client.get_bucket_encryption.return_value = {"ServerSideEncryptionConfiguration": {}}
        s3_client.get_bucket_versioning.return_value = {}
        s3_client.get_public_access_block.side_effect = make_client_error(
            "NoSuchPublicAccessBlockConfiguration"
        )
        s3_client.get_bucket_logging.return_value = {"LoggingEnabled": {}}
        s3_client.get_bucket_tagging.side_effect = make_client_error("NoSuchTagSet")

        checker = S3BucketComplianceCheck(s3_client, "partial-bucket")
        results = checker.run()

        assert len(results) == 5
        summary = checker.summary()
        assert summary["PASS"] == 2
        assert summary["FAIL"] == 3

    def test_print_report_output(self, s3_client, capsys):
        s3_client.get_bucket_encryption.return_value = {"ServerSideEncryptionConfiguration": {}}
        s3_client.get_bucket_versioning.return_value = {"Status": "Enabled"}
        s3_client.get_public_access_block.return_value = {"PublicAccessBlockConfiguration": {}}
        s3_client.get_bucket_logging.return_value = {"LoggingEnabled": {}}
        s3_client.get_bucket_tagging.return_value = {"TagSet": []}

        checker = S3BucketComplianceCheck(s3_client, "report-bucket")
        checker.run()
        checker.print_report()

        output = capsys.readouterr().out
        assert "report-bucket" in output
        assert "S3" in output
        assert "5 PASS" in output
