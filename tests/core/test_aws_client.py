"""Tests for the AWSClient core module."""

from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError, ProfileNotFound
import pytest

from cpe_project.core.aws_client import AWSClient


def make_client_error(code, message="test error"):
    return ClientError(
        {"Error": {"Code": code, "Message": message}}, "TestOp"
    )


class TestAWSClientInit:
    @patch("cpe_project.core.aws_client.boto3.Session")
    def test_creates_session_with_profile_and_region(self, mock_session):
        AWSClient(profile="dev", region="us-west-2")
        mock_session.assert_called_once_with(
            profile_name="dev", region_name="us-west-2"
        )

    @patch("cpe_project.core.aws_client.boto3.Session")
    def test_default_region(self, mock_session):
        AWSClient(profile="dev")
        mock_session.assert_called_once_with(
            profile_name="dev", region_name="us-east-1"
        )

    @patch("cpe_project.core.aws_client.boto3.Session")
    def test_invalid_profile_exits(self, mock_session):
        mock_session.side_effect = ProfileNotFound(profile="bad")
        with pytest.raises(SystemExit):
            AWSClient(profile="bad")


class TestAWSClientMethods:
    @patch("cpe_project.core.aws_client.boto3.Session")
    def test_client_returns_boto3_client(self, mock_session):
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        aws = AWSClient(profile="dev")
        result = aws.client("s3")
        assert result == mock_client

    @patch("cpe_project.core.aws_client.boto3.Session")
    def test_resource_returns_boto3_resource(self, mock_session):
        mock_resource = MagicMock()
        mock_session.return_value.resource.return_value = mock_resource
        aws = AWSClient(profile="dev")
        result = aws.resource("s3")
        assert result == mock_resource


class TestHandleClientError:
    def test_formats_error_with_context(self):
        err = make_client_error("AccessDenied", "Not authorized")
        result = AWSClient.handle_client_error(err, "my-bucket")
        assert "my-bucket" in result
        assert "AccessDenied" in result
        assert "Not authorized" in result

    def test_formats_error_without_context(self):
        err = make_client_error("NotFound", "Gone")
        result = AWSClient.handle_client_error(err)
        assert result == "[NotFound] Gone"
