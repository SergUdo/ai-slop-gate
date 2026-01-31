# Before start:
# export GITHUB_TOKEN=your_github_token
# export GITHUB_REPOSITORY=your_repo
# export PR_ID=your_pr_id

# Start test with:
# python -m scripts.test_pr_reporter

#!/usr/bin/env python3
import os
import logging
import sys
from typing import List, Optional
from ai_slop_gate.reporters.github_pr import GitHubPRReporter
from ai_slop_gate.domain.checks import CheckReport, CheckStatus, CheckAnnotation
from ai_slop_gate.domain.observation import Observation

# Налаштування логування
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("test_pr_reporter")

def log_step(step: str, message: str) -> None:
    logger.info(f"📌 STEP {step}: {message}")

def log_observation(observation: Observation) -> None:
    logger.debug(
        f"Observation: rule_id={observation.rule_id}, "
        f"category={observation.category}, signal={observation.signal}, "
        f"confidence={observation.confidence}, severity={observation.severity}, "
        f"message={observation.message}"
    )

def log_annotation(annotation: CheckAnnotation) -> None:
    logger.debug(
        f"Annotation: file={annotation.file}, line={annotation.line}, "
        f"level={annotation.level}, message={annotation.message}"
    )

def create_sample_observations() -> List[Observation]:
    log_step(1, "Creating sample observations")
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
    for obs in observations:
        log_observation(obs)
    return observations

def create_annotations(observations: List[Observation]) -> List[CheckAnnotation]:
    log_step(2, "Creating annotations from observations")
    annotations = [
        CheckAnnotation(
            file="config.js" if i == 0 else "app.js",
            line=12 if i == 0 else 45,
            level="failure" if obs.severity == "high" else "warning",
            message=obs.message
        ) for i, obs in enumerate(observations)
    ]
    for ann in annotations:
        log_annotation(ann)
    return annotations

def create_report(annotations: List[CheckAnnotation]) -> CheckReport:
    log_step(3, "Creating report")
    report = CheckReport(
        title="AI Slop Gate Analysis Results",
        status=CheckStatus.FAIL,
        summary="Automated review identified security risks and AI-generated patterns.",
        annotations=annotations
    )
    logger.debug(f"Report: title={report.title}, status={report.status}, summary={report.summary}")
    return report

def test_reporter(report: CheckReport, token: str, repo: str, pr_id: int) -> None:
    log_step(4, "Testing reporter")
    reporter = GitHubPRReporter(
        token=token,
        repo_name=repo,
        pr_id=pr_id,
    )

    print("\n" + "="*60)
    print("      DRY RUN: PR COMMENT PREVIEW")
    print("="*60)

    print(f"TITLE:   {report.title}")
    print(f"STATUS:  {report.status.value}")
    print(f"SUMMARY: {report.summary}")
    print("-" * 60)
    for i, ann in enumerate(report.annotations, 1):
        print(f"{i}. [{ann.level.upper()}] {ann.file}:{ann.line}")
        print(f"   Message: {ann.message}")

    if token != "DUMMY_TOKEN":
        print("\n🚀 Attempting to post to GitHub...")
        try:
            reporter.report(report)
            print("✅ Successfully posted to GitHub!")
        except Exception as e:
            logger.error(f"Failed to post to GitHub: {e}")
    else:
        print("\nℹ️  Skipping GitHub API call (using DUMMY_TOKEN).")
        print("To test live: export GITHUB_TOKEN=your_token && python -m scripts.test_pr_reporter")

    print("="*60 + "\n")

def main():
    try:
        observations = create_sample_observations()
        annotations = create_annotations(observations)
        report = create_report(annotations)

        token = os.getenv("GITHUB_TOKEN", "DUMMY_TOKEN")
        repo = os.getenv("GITHUB_REPOSITORY", "SergUdo/ai-slop-gate")
        pr_id = int(os.getenv("PR_ID", "1"))

        test_reporter(report, token, repo, pr_id)
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
