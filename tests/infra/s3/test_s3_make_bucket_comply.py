"""Tests for S3 bucket remediation."""

from unittest.mock import MagicMock
from botocore.exceptions import ClientError
import pytest

from cpe_project.core.compliance import Status
from cpe_project.infra.s3.s3_make_bucket_comply import S3BucketRemediation


def make_client_error(code, message="error"):
    return ClientError(
        {"Error": {"Code": code, "Message": message}}, "operation"
    )


@pytest.fixture
def s3_client():
    return MagicMock()


class TestFixEncryption:
    def test_enables_encryption(self, s3_client):
        s3_client.get_bucket_encryption.side_effect = make_client_error("NotFound")
        s3_client.put_bucket_encryption.return_value = {}
        r = S3BucketRemediation(s3_client, "bucket")
        result = r.fix_encryption()
        assert result.status == Status.REMEDIATED
        s3_client.put_bucket_encryption.assert_called_once()

    def test_error_on_failure(self, s3_client):
        s3_client.put_bucket_encryption.side_effect = make_client_error("AccessDenied")
        r = S3BucketRemediation(s3_client, "bucket")
        result = r.fix_encryption()
        assert result.status == Status.ERROR


class TestFixVersioning:
    def test_enables_versioning(self, s3_client):
        s3_client.put_bucket_versioning.return_value = {}
        r = S3BucketRemediation(s3_client, "bucket")
        result = r.fix_versioning()
        assert result.status == Status.REMEDIATED

    def test_error_on_failure(self, s3_client):
        s3_client.put_bucket_versioning.side_effect = make_client_error("AccessDenied")
        r = S3BucketRemediation(s3_client, "bucket")
        result = r.fix_versioning()
        assert result.status == Status.ERROR


class TestFixPublicAccessBlock:
    def test_blocks_public_access(self, s3_client):
        s3_client.put_public_access_block.return_value = {}
        r = S3BucketRemediation(s3_client, "bucket")
        result = r.fix_public_access_block()
        assert result.status == Status.REMEDIATED

    def test_error_on_failure(self, s3_client):
        s3_client.put_public_access_block.side_effect = make_client_error("AccessDenied")
        r = S3BucketRemediation(s3_client, "bucket")
        result = r.fix_public_access_block()
        assert result.status == Status.ERROR


class TestFixLogging:
    def test_enables_logging(self, s3_client):
        s3_client.put_bucket_logging.return_value = {}
        r = S3BucketRemediation(s3_client, "bucket")
        result = r.fix_logging()
        assert result.status == Status.REMEDIATED

    def test_error_on_failure(self, s3_client):
        s3_client.put_bucket_logging.side_effect = make_client_error("AccessDenied")
        r = S3BucketRemediation(s3_client, "bucket")
        result = r.fix_logging()
        assert result.status == Status.ERROR


class TestFixTags:
    def test_applies_tags(self, s3_client):
        s3_client.put_bucket_tagging.return_value = {}
        r = S3BucketRemediation(s3_client, "bucket")
        result = r.fix_tags()
        assert result.status == Status.REMEDIATED
        call_args = s3_client.put_bucket_tagging.call_args
        tags = call_args.kwargs["Tagging"]["TagSet"]
        assert len(tags) == 2

    def test_error_on_failure(self, s3_client):
        s3_client.put_bucket_tagging.side_effect = make_client_error("AccessDenied")
        r = S3BucketRemediation(s3_client, "bucket")
        result = r.fix_tags()
        assert result.status == Status.ERROR


class TestFullRemediation:
    def test_check_and_remediate(self, s3_client):
        # All checks fail
        s3_client.get_bucket_encryption.side_effect = make_client_error("NotFound")
        s3_client.get_bucket_versioning.return_value = {}
        s3_client.get_public_access_block.side_effect = make_client_error(
            "NoSuchPublicAccessBlockConfiguration"
        )
        s3_client.get_bucket_logging.return_value = {}
        s3_client.get_bucket_tagging.side_effect = make_client_error("NoSuchTagSet")

        # All remediations succeed
        s3_client.put_bucket_encryption.return_value = {}
        s3_client.put_bucket_versioning.return_value = {}
        s3_client.put_public_access_block.return_value = {}
        s3_client.put_bucket_logging.return_value = {}
        s3_client.put_bucket_tagging.return_value = {}

        r = S3BucketRemediation(s3_client, "non-compliant")
        results = r.run(remediate=True)

        # 5 checks + 5 remediations
        assert len(results) == 10
        summary = r.summary()
        assert summary["FAIL"] == 5
        assert summary["REMEDIATED"] == 5
