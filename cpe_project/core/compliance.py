"""Base class for compliance checks and remediation actions."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from cpe_project.core.logger import get_logger


class Status(Enum):
    """Result status for a single compliance check."""
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"
    REMEDIATED = "REMEDIATED"


@dataclass
class ComplianceResult:
    """Outcome of a single compliance check."""
    control: str
    status: Status
    resource: str
    message: str = ""


class ComplianceCheck:
    """Base class for a set of compliance checks against one AWS resource.

    Subclasses implement check and/or remediation methods, then register them
    via :meth:`add_check` and :meth:`add_remediation`. Running :meth:`run`
    executes all registered checks and returns a summary.

    Example::

        class S3BucketCheck(ComplianceCheck):
            def __init__(self, s3_client, bucket_name):
                super().__init__(resource_id=bucket_name, service="S3")
                self.s3 = s3_client
                self.bucket = bucket_name
                self.add_check("S3.4", self.check_encryption)

            def check_encryption(self):
                enc = self.s3.get_bucket_encryption(Bucket=self.bucket)
                return ComplianceResult(
                    control="S3.4", status=Status.PASS,
                    resource=self.bucket,
                    message="Server-side encryption enabled"
                )
    """

    def __init__(self, resource_id: str, service: str):
        self.resource_id = resource_id
        self.service = service
        self.log = get_logger(f"{service}Compliance")
        self._checks: list[tuple[str, callable]] = []
        self._remediations: list[tuple[str, callable]] = []
        self.results: list[ComplianceResult] = field(default_factory=list)
        self.results = []

    def add_check(self, control: str, fn: callable) -> None:
        """Register a check function for the given control ID."""
        self._checks.append((control, fn))

    def add_remediation(self, control: str, fn: callable) -> None:
        """Register a remediation function for the given control ID."""
        self._remediations.append((control, fn))

    def run(self, remediate: bool = False) -> list[ComplianceResult]:
        """Execute all registered checks. If *remediate* is True, run
        remediation for any failed checks that have a registered fix."""
        self.results = []
        for control, check_fn in self._checks:
            result = check_fn()
            self.results.append(result)
            self.log.info(
                "[%s] %s — %s: %s",
                result.status.value, control,
                self.resource_id, result.message,
            )

        if remediate:
            failed = {r.control for r in self.results if r.status == Status.FAIL}
            for control, fix_fn in self._remediations:
                if control in failed:
                    result = fix_fn()
                    self.results.append(result)
                    self.log.info(
                        "[%s] %s — %s: %s",
                        result.status.value, control,
                        self.resource_id, result.message,
                    )

        return self.results

    def summary(self) -> dict[str, int]:
        """Return counts by status."""
        counts: dict[str, int] = {}
        for r in self.results:
            counts[r.status.value] = counts.get(r.status.value, 0) + 1
        return counts

    def print_report(self) -> None:
        """Print a formatted compliance report to stdout."""
        print(f"\n{'='*60}")
        print(f"  Compliance Report: {self.service} — {self.resource_id}")
        print(f"{'='*60}")
        for r in self.results:
            icon = {"PASS": "+", "FAIL": "!", "ERROR": "?", "REMEDIATED": "*"}
            print(f"  [{icon.get(r.status.value, ' ')}] {r.control}: {r.message}")
        counts = self.summary()
        print(f"{'─'*60}")
        parts = [f"{v} {k}" for k, v in counts.items()]
        print(f"  Summary: {', '.join(parts)}")
        print(f"{'='*60}\n")
