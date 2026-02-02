import importlib
import sys
import types

import pytest


def _make_fake_github_module(monkeypatch):
    mod = types.SimpleNamespace()
    class DummyRepo:
        def __init__(self, *a, **k):
            self.full_name = "org/repo"
        def create_check_run(self, **kwargs):
            return True
        def get_pull(self, pid):
            class PR:
                number = pid
                def create_issue_comment(self, body):
                    return True
            return PR()

    def Github(token):
        class C:
            def __init__(self, token):
                pass
            def get_repo(self, repo):
                return DummyRepo()
        return C(token)

    fake = types.ModuleType("github")
    fake.Github = Github
    fake.GithubException = Exception
    monkeypatch.setitem(sys.modules, "github", fake)


def test_github_checks_reporter_init_and_report(monkeypatch):
    _make_fake_github_module(monkeypatch)
    # import inside to ensure fake module is used
    from ai_slop_gate.reporters.github_checks import GitHubChecksReporter
    from ai_slop_gate.domain.checks import CheckReport, CheckAnnotation, CheckStatus

    reporter = GitHubChecksReporter(token="t", repo="org/repo", sha="deadbeef")
    report = CheckReport(title="T", summary="S", status=CheckStatus.FAIL, annotations=[CheckAnnotation(file="a.py", line=1, message="m", level="failure")])
    reporter.report(report)


def test_github_pr_reporter_post_comment(monkeypatch):
    _make_fake_github_module(monkeypatch)
    # ensure module import uses fake github
    from ai_slop_gate.reporters.github_pr import GitHubPRReporter
    from ai_slop_gate.domain.checks import CheckReport, CheckAnnotation, CheckStatus

    # create with token to trigger client creation
    reporter = GitHubPRReporter(token="t", repo_name="org/repo", pr_id=1)
    report = CheckReport(title="T", summary="S", status=CheckStatus.FAIL, annotations=[CheckAnnotation(file="a.py", line=1, message="m", level="failure")])
    # Should not raise
    reporter.report(report)
