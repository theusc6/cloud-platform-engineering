"""Tests for the ComplianceCheck base class."""

from cpe_project.core.compliance import ComplianceCheck, ComplianceResult, Status


def _pass_result(control="TEST.1"):
    return ComplianceResult(
        control=control, status=Status.PASS,
        resource="test-resource", message="All good",
    )


def _fail_result(control="TEST.1"):
    return ComplianceResult(
        control=control, status=Status.FAIL,
        resource="test-resource", message="Not compliant",
    )


def _remediated_result(control="TEST.1"):
    return ComplianceResult(
        control=control, status=Status.REMEDIATED,
        resource="test-resource", message="Fixed",
    )


class TestComplianceResult:
    def test_pass_status(self):
        r = _pass_result()
        assert r.status == Status.PASS
        assert r.control == "TEST.1"

    def test_fail_status(self):
        r = _fail_result()
        assert r.status == Status.FAIL


class TestComplianceCheck:
    def test_run_executes_all_checks(self):
        checker = ComplianceCheck(resource_id="res-1", service="Test")
        checker.add_check("A", lambda: _pass_result("A"))
        checker.add_check("B", lambda: _fail_result("B"))

        results = checker.run()
        assert len(results) == 2
        assert results[0].status == Status.PASS
        assert results[1].status == Status.FAIL

    def test_run_with_remediation(self):
        checker = ComplianceCheck(resource_id="res-1", service="Test")
        checker.add_check("A", lambda: _fail_result("A"))
        checker.add_remediation("A", lambda: _remediated_result("A"))

        results = checker.run(remediate=True)
        assert len(results) == 2
        assert results[0].status == Status.FAIL
        assert results[1].status == Status.REMEDIATED

    def test_remediation_skipped_for_passing_checks(self):
        checker = ComplianceCheck(resource_id="res-1", service="Test")
        checker.add_check("A", lambda: _pass_result("A"))
        checker.add_remediation("A", lambda: _remediated_result("A"))

        results = checker.run(remediate=True)
        assert len(results) == 1
        assert results[0].status == Status.PASS

    def test_summary_counts(self):
        checker = ComplianceCheck(resource_id="res-1", service="Test")
        checker.add_check("A", lambda: _pass_result("A"))
        checker.add_check("B", lambda: _fail_result("B"))
        checker.add_check("C", lambda: _pass_result("C"))
        checker.run()

        summary = checker.summary()
        assert summary == {"PASS": 2, "FAIL": 1}

    def test_print_report(self, capsys):
        checker = ComplianceCheck(resource_id="my-bucket", service="S3")
        checker.add_check("S3.4", lambda: _pass_result("S3.4"))
        checker.run()
        checker.print_report()

        captured = capsys.readouterr()
        assert "S3" in captured.out
        assert "my-bucket" in captured.out
        assert "PASS" in captured.out


class TestStatusEnum:
    def test_all_values(self):
        assert Status.PASS.value == "PASS"
        assert Status.FAIL.value == "FAIL"
        assert Status.ERROR.value == "ERROR"
        assert Status.REMEDIATED.value == "REMEDIATED"
