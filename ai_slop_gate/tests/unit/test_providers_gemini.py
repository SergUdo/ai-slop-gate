# tests/test_providers_gemini.py
from unittest.mock import MagicMock, patch
from ai_slop_gate.providers.gemini import GeminiProvider

def test_gemini_provider():
    args = MagicMock()
    args.model = "gemini-2.5-flash"
    args.api_key = "test_api_key"
    args.github_repo = "test-repo"
    args.github_sha = "abc123"
    args.pr_id = "123"

    with patch("google.generativeai.GenerativeModel") as mock_model_class:
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        mock_response = MagicMock()
        mock_response.text = '{"category": "quality", "signal": "ai_indicator", "confidence": 0.9, "severity": "high", "message": "Test message"}'
        mock_model.generate_content.return_value = mock_response

        provider = GeminiProvider(args)
        observations = provider.analyze("test code")

        assert len(observations.observations) == 1
        assert observations.observations[0].category == "quality"
