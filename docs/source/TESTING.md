# 🧪 Testing Guide

Complete guide for testing ai-slop-gate.

---

## Quick Start

```bash
# Run all tests
python -m pytest ai_slop_gate/tests -v

# Run with coverage
python -m pytest ai_slop_gate/tests \
  --cov=ai_slop_gate \
  --cov-report=term-missing \
  --cov-report=html

# View HTML coverage report
xdg-open htmlcov/index.html  # Linux
open htmlcov/index.html       # macOS
start htmlcov\index.html      # Windows
```

---

## Test Structure

```
ai_slop_gate/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures
│   ├── test_cli.py              # CLI tests
│   ├── test_providers/
│   │   ├── test_static.py       # Static analysis tests
│   │   ├── test_gemini.py       # Gemini provider tests
│   │   ├── test_groq.py         # Groq provider tests
│   │   └── test_ollama.py       # Ollama provider tests
│   ├── test_compliance/
│   │   ├── test_license.py      # License checks
│   │   ├── test_gdpr.py         # GDPR compliance
│   │   └── test_supply_chain.py # Supply chain tests
│   └── test_integration/
│       ├── test_github.py       # GitHub integration
│       ├── test_gitlab.py       # GitLab integration
│       └── test_cache.py        # Cache integration
```

---

## Running Tests

### All Tests

```bash
python -m pytest ai_slop_gate/tests -v
```

---

### Specific Test File

```bash
# Test static provider
python -m pytest ai_slop_gate/tests/test_providers/test_static.py -v

# Test CLI
python -m pytest ai_slop_gate/tests/test_cli.py -v
```

---

### Specific Test Function

```bash
python -m pytest ai_slop_gate/tests/test_cli.py::test_run_static -v
```

---

### By Marker

```bash
# Only unit tests
python -m pytest -m unit

# Only integration tests
python -m pytest -m integration

# Skip slow tests
python -m pytest -m "not slow"
```

---

## Test Coverage

### Generate Coverage Report

```bash
source .venv/bin/activate

python -m pytest ai_slop_gate/tests \
  --cov=ai_slop_gate \
  --cov-report=term-missing \
  --cov-report=html \
  --cov-report=xml
```

---

### View Coverage

```bash
# Terminal report (summary)
python -m pytest --cov=ai_slop_gate --cov-report=term

# HTML report (detailed)
python -m pytest --cov=ai_slop_gate --cov-report=html
xdg-open htmlcov/index.html

# XML report (for CI/CD)
python -m pytest --cov=ai_slop_gate --cov-report=xml
```

---

### Coverage Targets

| Component | Target | Current |
|-----------|--------|---------|
| Overall | 80% | Check `htmlcov/index.html` |
| Core CLI | 90% | - |
| Providers | 75% | - |
| Compliance | 85% | - |

---

## Cache Integration Tests

### Quick Test (30 seconds)

```bash
./scripts/quick_cache_test.sh
```

**Expected output:**
```
✅ Cache system initialized
✅ First run: API called
✅ Second run: Cache hit
✅ All integration tests passed!
```

---

### Full Smoke Test

Requires API keys:

```bash
export GEMINI_API_KEY="your-key"
./scripts/verify_cache_v2.sh
```

**Tests:**
- Cache initialization
- First run (API call)
- Second run (cache hit)
- Cache invalidation
- Cache statistics

---

## Test Demo Repository

Test detection on intentionally bad code:

```bash
git clone https://github.com/SergUdo/slop_test
cd slop_test

# Run static analysis
python -m ai_slop_gate.cli run --provider static --path .

# Run LLM analysis
python -m ai_slop_gate.cli run --provider gemini --llm-local --path .
```

**Expected:** Multiple violations detected (secrets, AI slop, license issues)

---

## Writing Tests

### Unit Test Example

```python
import pytest
from ai_slop_gate.providers.static import StaticProvider

def test_secret_detection():
    """Test that hardcoded secrets are detected."""
    code = 'API_KEY = "sk-1234567890abcdef"'
    
    provider = StaticProvider()
    results = provider.analyze(code)
    
    assert len(results) > 0
    assert any('secret' in r.message.lower() for r in results)
```

---

### Integration Test Example

```python
import pytest
from ai_slop_gate.cli import run_analysis

@pytest.mark.integration
def test_full_analysis(tmp_path):
    """Test full analysis pipeline."""
    # Create test file
    test_file = tmp_path / "test.py"
    test_file.write_text('eval("malicious_code")')
    
    # Run analysis
    results = run_analysis(
        provider='static',
        path=str(tmp_path)
    )
    
    assert results.has_violations()
    assert 'eval' in results.violations[0].message
```

---

### Cache Test Example

```python
import pytest
from ai_slop_gate.cache import LLMCache

def test_cache_hit():
    """Test cache hit on repeated analysis."""
    cache = LLMCache()
    
    # First call
    result1 = cache.get_or_compute(
        key='test_key',
        compute_fn=lambda: expensive_llm_call()
    )
    
    # Second call (should use cache)
    result2 = cache.get_or_compute(
        key='test_key',
        compute_fn=lambda: expensive_llm_call()
    )
    
    assert result1 == result2
    assert cache.stats['hits'] == 1
```

---

## Test Fixtures

### Common Fixtures (`conftest.py`)

```python
import pytest
from pathlib import Path

@pytest.fixture
def test_project(tmp_path):
    """Create a temporary test project."""
    project = tmp_path / "test_project"
    project.mkdir()
    
    # Create test files
    (project / "main.py").write_text("print('hello')")
    (project / "policy.yml").write_text("enforcement: advisory")
    
    return project

@pytest.fixture
def mock_api_response():
    """Mock LLM API response."""
    return {
        'severity': 'high',
        'confidence': 0.9,
        'message': 'AI-generated code detected'
    }
```

---

## Mocking External APIs

### Mock Gemini API

```python
import pytest
from unittest.mock import patch

@pytest.mark.unit
def test_gemini_provider(mock_api_response):
    """Test Gemini provider with mocked API."""
    with patch('ai_slop_gate.providers.gemini.call_api') as mock:
        mock.return_value = mock_api_response
        
        provider = GeminiProvider()
        result = provider.analyze("test code")
        
        assert result.severity == 'high'
        mock.assert_called_once()
```

---

### Mock GitHub API

```python
@pytest.mark.integration
def test_github_comment():
    """Test PR comment posting."""
    with patch('github.PullRequest.create_comment') as mock:
        post_pr_comment(
            repo='owner/repo',
            pr_id=123,
            message='Test comment'
        )
        
        mock.assert_called_once()
```

---

## Performance Testing

### Benchmark Test

```python
import pytest
import time

@pytest.mark.benchmark
def test_static_analysis_performance(benchmark):
    """Benchmark static analysis speed."""
    def analyze():
        provider = StaticProvider()
        return provider.analyze(large_codebase)
    
    result = benchmark(analyze)
    assert result.duration < 5.0  # Must complete in 5s
```

---

### Cache Performance

```bash
# Measure cache improvement
./scripts/benchmark_cache.sh

# Expected output:
# Without cache: 15.2s
# With cache: 0.8s
# Speedup: 19x
```

---

## Test Markers

### Available Markers

```python
@pytest.mark.unit          # Unit tests (fast, no external deps)
@pytest.mark.integration   # Integration tests (may need API keys)
@pytest.mark.slow          # Slow tests (>5 seconds)
@pytest.mark.benchmark     # Performance benchmarks
@pytest.mark.requires_api  # Requires API keys
```

---

### Run by Marker

```bash
# Only fast unit tests
pytest -m "unit and not slow"

# Integration tests only
pytest -m integration

# Skip tests requiring API
pytest -m "not requires_api"
```

---

## CI/CD Testing

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest pytest-cov
      
      - name: Run tests
        run: |
          python -m pytest ai_slop_gate/tests \
            --cov=ai_slop_gate \
            --cov-report=xml \
            --cov-report=term
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

---

### GitLab CI

```yaml
test:
  stage: test
  image: python:3.11
  script:
    - pip install -e .
    - pip install pytest pytest-cov
    - pytest ai_slop_gate/tests --cov=ai_slop_gate --cov-report=term
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

---

## Test Data

### Fixtures Location

```
ai_slop_gate/tests/fixtures/
├── code_samples/
│   ├── good_code.py
│   ├── bad_code.py
│   ├── ai_slop.py
│   └── secrets.py
├── policies/
│   ├── strict.yml
│   ├── advisory.yml
│   └── permissive.yml
└── responses/
    ├── gemini_response.json
    └── groq_response.json
```

---

### Using Test Fixtures

```python
import pytest
from pathlib import Path

@pytest.fixture
def ai_slop_sample():
    """Load AI slop code sample."""
    fixture_path = Path(__file__).parent / 'fixtures' / 'code_samples' / 'ai_slop.py'
    return fixture_path.read_text()

def test_ai_slop_detection(ai_slop_sample):
    provider = GeminiProvider()
    result = provider.analyze(ai_slop_sample)
    assert result.has_ai_slop
```

---

## Debugging Tests

### Run with Verbose Output

```bash
pytest -vv
```

---

### Show Print Statements

```bash
pytest -s
```

---

### Stop on First Failure

```bash
pytest -x
```

---

### Run Last Failed Tests

```bash
pytest --lf
```

---

### Debug with PDB

```python
def test_something():
    import pdb; pdb.set_trace()
    assert some_condition
```

Or:

```bash
pytest --pdb  # Drop into debugger on failure
```

---

## Test Best Practices

### 1. Keep Tests Fast

```python
# ✅ GOOD: Mock external calls
@patch('ai_slop_gate.providers.gemini.call_api')
def test_provider(mock_api):
    mock_api.return_value = {...}

# ❌ BAD: Real API calls in tests
def test_provider():
    result = call_real_api()  # Slow and flaky
```

---

### 2. Test Edge Cases

```python
def test_empty_input():
    assert analyze("") == []

def test_large_input():
    assert analyze("x" * 1_000_000) is not None

def test_unicode():
    assert analyze("🚀 code") is not None
```

---

### 3. Use Descriptive Names

```python
# ✅ GOOD
def test_secret_detection_in_environment_variables():
    ...

# ❌ BAD
def test_secrets():
    ...
```

---

### 4. One Assertion Per Test

```python
# ✅ GOOD
def test_severity_is_high():
    assert result.severity == 'high'

def test_confidence_is_above_threshold():
    assert result.confidence > 0.8

# ❌ BAD
def test_result():
    assert result.severity == 'high'
    assert result.confidence > 0.8
    assert result.message == 'test'
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError"

**Solution:** Install in editable mode

```bash
pip install -e .
```

---

### Issue: Tests hang indefinitely

**Solution:** Use timeout

```bash
pytest --timeout=60  # 60 second timeout per test
```

---

### Issue: "No tests collected"

**Solution:** Check test discovery

```bash
# Ensure test files start with "test_"
# Ensure test functions start with "test_"
pytest --collect-only  # See what pytest finds
```

---

### Issue: Cache tests failing

**Solution:** Clear cache before tests

```bash
rm -rf .ai-slop-cache/
pytest ai_slop_gate/tests/test_integration/test_cache.py
```

---

## Coverage Goals

### Priority Areas

1. **Core CLI** (90%+)
   - Command parsing
   - Configuration loading
   - Provider orchestration

2. **Static Providers** (85%+)
   - Secret detection
   - Dangerous function detection
   - License checks

3. **LLM Providers** (75%+)
   - API integration
   - Response parsing
   - Cache integration

4. **Compliance** (85%+)
   - GDPR checks
   - License validation
   - Supply chain audit

---

## Related Documentation

- [CLI Reference](CLI_REFERENCE.md) — Command-line options
- [Docker Guide](DOCKER.md) — Docker testing
- [Cache Guide](CACHE.md) — Cache testing
- [Development Setup](../docs/source/DEV_SETUP.md) — Development environment

---

## Support

Testing issues?
1. Check [GitHub Issues](https://github.com/SergUdo/ai-slop-gate/issues)
2. Read [Documentation](https://ai-slop-gate.readthedocs.io/)
3. Ask in [Discussions](https://github.com/SergUdo/ai-slop-gate/discussions)