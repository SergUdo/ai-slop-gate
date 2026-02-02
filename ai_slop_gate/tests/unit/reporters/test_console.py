from ai_slop_gate.reporters.console import ConsoleReporter
from ai_slop_gate.domain.checks import CheckReport, CheckAnnotation, CheckStatus


def make_report(short=True):
    anns = [CheckAnnotation(file="a.py", line=10, message="m1", level="warning")]
    status = CheckStatus.FAIL if not short else CheckStatus.PASS
    return CheckReport(title="T", summary="S", status=status, annotations=anns, reasons=["r1"])


def test_console_report_short(capsys):
    r = ConsoleReporter(verbose=False)
    report = make_report(short=True)
    r.report(report)
    out = capsys.readouterr().out
    assert "AI SLOP GATE REPORT" in out
    assert "Total findings" in out


def test_console_report_verbose(capsys):
    r = ConsoleReporter(verbose=True)
    report = make_report(short=False)
    r.report(report)
    out = capsys.readouterr().out
    assert "VERBOSE MODE" in out
    assert "Annotations:" in out
