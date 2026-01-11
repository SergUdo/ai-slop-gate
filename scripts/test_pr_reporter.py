# python -m scripts.test_pr_reporter

import os
import logging
from ai_slop_gate.reporters.github_pr import GitHubPRReporter
from ai_slop_gate.domain.checks import CheckReport, CheckStatus, CheckAnnotation
from ai_slop_gate.domain.observation import Observation

# Basic logging setup to see what's happening
logging.basicConfig(level=logging.INFO)

def main():
    # 1. Create Observations (following your strict Observation class)
    observations = [
        Observation(
            rule_id="sec_001",
            category="security",
            signal="negative",
            confidence=0.9,
            message="Hardcoded API key found in config.js:12",
            severity="high"
        ),
        Observation(
            rule_id="slop_001",
            category="quality",
            signal="ai_pattern",
            confidence=0.85,
            message="Generic function name 'foo' detected in app.js:45",
            severity="low"
        ),
    ]

    # 2. Create Annotations (only using supported arguments)
    # Based on your error, we removed 'raw_details'
    annotations = [
        CheckAnnotation(
            file="config.js" if i == 0 else "app.js",
            line=12 if i == 0 else 45,
            level="failure" if obs.severity == "high" else "warning",
            message=obs.message
        ) for i, obs in enumerate(observations)
    ]

    # 3. Assemble the Report
    report = CheckReport(
        title="AI Slop Gate Analysis Results",
        status=CheckStatus.FAIL,
        summary="Automated review identified security risks and AI-generated patterns.",
        annotations=annotations
    )

    # 4. Initialize the Reporter
    # It will run in 'offline mode' if GITHUB_TOKEN is not provided
    token = os.getenv("GITHUB_TOKEN", "DUMMY_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY", "SergUdo/ai-slop-gate")
    pr_id = os.getenv("PR_ID", "1")

    reporter = GitHubPRReporter(
        token=token,
        repo_name=repo,
        pr_id=int(pr_id),
    )

    print("\n" + "="*40)
    print("      DRY RUN: PR COMMENT PREVIEW")
    print("="*40)
    
    # Visual check of what will be sent
    print(f"TITLE:   {report.title}")
    print(f"STATUS:  {report.status.value}")
    print(f"SUMMARY: {report.summary}")
    print("-" * 40)
    for i, ann in enumerate(report.annotations, 1):
        print(f"{i}. [{ann.level.upper()}] {ann.file}:{ann.line}")
        print(f"   Message: {ann.message}")
    
    # Attempt to post if token is real
    if token != "DUMMY_TOKEN":
        print("\n🚀 Posting to GitHub...")
        reporter.report(report)
    else:
        print("\nℹ️  Skipping GitHub API call (using DUMMY_TOKEN).")
        print("To test live: export GITHUB_TOKEN=your_token && python -m scripts.test_pr_reporter")

    print("="*40 + "\n")

if __name__ == "__main__":
    main()