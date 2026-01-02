# python -m scripts.test_pr_reporter

from ai_slop_gate.reporters.github import GitHubPRReporter
from ai_slop_gate.domain.decision import Decision, DecisionMode
from ai_slop_gate.domain.observation import Observation


def main():
    decision = Decision(
        mode=DecisionMode.BLOCKING,
        reasons=[
            "Hardcoded secret detected",
            "Insecure default configuration detected",
        ],
    )

    observations = [
        Observation(
            category="security",
            signal="negative",
            confidence=0.9,
            message="Hardcoded API key found",
            evidence={"file": "config.js", "line": 12},
        ),
        Observation(
            category="security",
            signal="negative",
            confidence=0.9,
            message="Hardcoded API key found", # duplicate
            evidence={"file": "config.js", "line": 12},
        ),
        Observation(
            category="dev_in_prod",
            signal="negative",
            confidence=0.8,
            message="console.log found in production code",
            evidence={"file": "app.js", "line": 45},
        ),
    ]

    reporter = GitHubPRReporter(
        token="DUMMY_TOKEN",
        repo="dummy/repo",
        pr_id=1,
    )

    comment = reporter._format_comment(decision, observations)

    print("\n===== GENERATED PR COMMENT =====\n")
    print(comment)
    print("\n===== END =====\n")


if __name__ == "__main__":
    main()