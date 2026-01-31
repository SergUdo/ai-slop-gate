import sys
from typing import Optional
from ai_slop_gate.domain.checks import CheckReport, CheckAnnotation


class ConsoleReporter:
    """
    Local console reporter for AI Slop Gate.
    Supports:
    - short summary mode
    - full verbose mode (compliance, rules, observations, reasons, annotations)
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def report(self, report: CheckReport):
        """
        Print the report to stdout.
        """

        print("\n=== AI SLOP GATE REPORT ===")
        print(f"Title: {report.title}")
        print(f"Summary: {report.summary}")
        print(f"Verdict: {report.status.value.upper()}")
        print(f"Total findings: {len(report.annotations)}")

        if not self.verbose:
            # Short mode
            print("\nIssues:")
            if not report.annotations:
                print("  (none)")
            else:
                for ann in report.annotations:
                    level = ann.level.upper()
                    print(f"  {level}: {ann.file}:{ann.line} — {ann.message}")
            print("\n=== END OF REPORT ===\n")
            return

        # Verbose mode
        print("\n=== VERBOSE MODE ===")

        # Observations (annotations are derived from observations)
        print("\nAnnotations:")
        if not report.annotations:
            print("  (none)")
        else:
            for ann in report.annotations:
                print(f"  - {ann.file}:{ann.line} [{ann.level}] {ann.message}")

        # Reasons (policy engine explanations)
        print("\nReasons:")
        if not report.reasons:
            print("  (none)")
        else:
            for r in report.reasons:
                print(f"  - {r}")

        print("\n=== END OF VERBOSE REPORT ===\n")
