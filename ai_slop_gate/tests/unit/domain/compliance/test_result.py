from ai_slop_gate.domain.compliance.result import (
    ComplianceIssue,
    ComplianceResult,
)

def test_compliance_result_has_issues():
    issue = ComplianceIssue(
        id="MIT",
        license="MIT",
        severity="low",
        message="MIT license detected",
    )

    result = ComplianceResult(issues=[issue])
    assert result.has_issues is True
