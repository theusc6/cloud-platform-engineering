"""Shared AWS session and client management with retry logic."""

import sys
import boto3
from botocore.config import Config
from botocore.exceptions import (
    ClientError,
    NoCredentialsError,
    ProfileNotFound,
)

from cpe_project.core.logger import get_logger

DEFAULT_RETRY_CONFIG = Config(
    retries={"max_attempts": 3, "mode": "adaptive"}
)


class AWSClient:
    """Manages a boto3 session and provides pre-configured service clients.

    Usage::

        aws = AWSClient(profile="my-sso-profile", region="us-east-1")
        s3 = aws.client("s3")
        ec2 = aws.client("ec2")
    """

    def __init__(
        self,
        profile: str,
        region: str = "us-east-1",
        retry_config: Config | None = None,
    ):
        self.log = get_logger(self.__class__.__name__)
        self._retry_config = retry_config or DEFAULT_RETRY_CONFIG
        try:
            self._session = boto3.Session(
                profile_name=profile, region_name=region
            )
        except ProfileNotFound:
            self.log.error("AWS profile '%s' not found.", profile)
            sys.exit(1)
        self.log.info(
            "Session created (profile=%s, region=%s)", profile, region
        )

    def client(self, service: str):
        """Return a boto3 client for *service* with retry config applied."""
        return self._session.client(service, config=self._retry_config)

    def resource(self, service: str):
        """Return a boto3 resource for *service*."""
        return self._session.resource(service, config=self._retry_config)

    @staticmethod
    def handle_client_error(err: ClientError, context: str = "") -> str:
        """Extract a human-readable message from a ClientError.

        Returns the formatted error string (also logs it).
        """
        code = err.response["Error"]["Code"]
        message = err.response["Error"]["Message"]
        prefix = f"{context}: " if context else ""
        return f"{prefix}[{code}] {message}"
