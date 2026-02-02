import tempfile
from ai_slop_gate.providers.eslint import ESLintProvider


def test_eslint_provider_collect_no_errors(tmp_path):
    # Call collect in an empty temp dir; this should not raise and should return ProviderObservation
    p = ESLintProvider()
    res = p.collect(str(tmp_path))
    assert res.provider == "eslint"
    assert isinstance(res.raw_text, str)
