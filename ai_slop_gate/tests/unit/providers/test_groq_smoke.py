"""
Smoke tests for Groq provider.
Ensures:
- JSON parsing works correctly
- Retry logic functions properly
- Observations match expected schema
- Error handling is robust
"""
import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from ai_slop_gate.providers.llm.groq import GroqProvider
from ai_slop_gate.providers.base import ProviderObservation


@pytest.fixture
def groq_provider():
    """Create a Groq provider instance with mocked API key."""
    with patch.dict('os.environ', {'SLOPE_GATE_GROQ': 'test-api-key'}):
        provider = GroqProvider(model="llama-3.3-70b-versatile")
        return provider


class TestGroqProviderBasics:
    """Test basic Groq provider functionality."""

    def test_groq_provider_initialization(self):
        """Test that Groq provider initializes with proper attributes."""
        with patch.dict('os.environ', {'SLOPE_GATE_GROQ': 'test-key'}):
            provider = GroqProvider(model="test-model")
            
            assert provider.name == "groq"
            assert provider.kind == "llm"
            assert provider.model == "test-model"
            assert provider.api_key == "test-key"
            assert provider.url == "https://api.groq.com/openai/v1/chat/completions"

    def test_groq_provider_missing_api_key(self):
        """Test that missing API key raises ValueError."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="SLOPE_GATE_GROQ is missing"):
                GroqProvider(model="test-model")

    def test_groq_collect_returns_not_supported(self, groq_provider):
        """Test that collect() returns appropriate message for LLM provider."""
        result = groq_provider.collect()
        
        assert isinstance(result, ProviderObservation)
        assert result.provider == "groq"
        assert result.observations == []
        assert "LLM provider does not support collect()" in result.raw_text


class TestGroqAnalyzeJsonParsing:
    """Test JSON parsing in Groq analyze method."""

    def test_groq_analyze_valid_json_response(self, groq_provider):
        """Test parsing valid JSON response from Groq API."""
        mock_response = {
            'choices': [
                {
                    'message': {
                        'content': json.dumps([
                            {
                                'category': 'quality',
                                'signal': 'generic_placeholder',
                                'confidence': 0.85,
                                'severity': 'medium',
                                'message': 'Generic error handling',
                                'line': 42
                            }
                        ])
                    }
                }
            ]
        }

        with patch('ai_slop_gate.providers.llm.groq.requests.post') as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = Mock()

            result = groq_provider.analyze("test code", input_file="test.py")

            assert isinstance(result, ProviderObservation)
            assert result.provider == "groq"
            assert len(result.observations) == 1
            
            obs = result.observations[0]
            assert obs.category == "quality"
            assert obs.signal == "generic_placeholder"
            assert obs.confidence == 0.85
            assert obs.severity == "medium"

    def test_groq_analyze_json_with_markdown_blocks(self, groq_provider):
        """Test parsing JSON wrapped in markdown code blocks."""
        json_data = [
            {
                'category': 'quality',
                'signal': 'slop_detected',
                'confidence': 0.9,
                'severity': 'high',
                'message': 'AI-generated placeholder code',
                'line': 10
            }
        ]
        
        mock_response = {
            'choices': [
                {
                    'message': {
                        'content': f"```json\n{json.dumps(json_data)}\n```"
                    }
                }
            ]
        }

        with patch('ai_slop_gate.providers.llm.groq.requests.post') as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = Mock()

            result = groq_provider.analyze("test code", input_file="test.py")

            assert len(result.observations) == 1
            assert result.observations[0].signal == "slop_detected"

    def test_groq_analyze_empty_array_response(self, groq_provider):
        """Test handling of empty JSON array (no issues found)."""
        mock_response = {
            'choices': [
                {
                    'message': {
                        'content': json.dumps([])
                    }
                }
            ]
        }

        with patch('ai_slop_gate.providers.llm.groq.requests.post') as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = Mock()

            result = groq_provider.analyze("clean code", input_file="test.py")

            assert isinstance(result, ProviderObservation)
            assert result.observations == []

    def test_groq_analyze_multiple_observations(self, groq_provider):
        """Test parsing multiple observations from single response."""
        mock_response = {
            'choices': [
                {
                    'message': {
                        'content': json.dumps([
                            {
                                'category': 'quality',
                                'signal': 'placeholder_one',
                                'confidence': 0.8,
                                'severity': 'medium',
                                'message': 'First issue',
                                'line': 5
                            },
                            {
                                'category': 'architecture',
                                'signal': 'placeholder_two',
                                'confidence': 0.75,
                                'severity': 'low',
                                'message': 'Second issue',
                                'line': 15
                            }
                        ])
                    }
                }
            ]
        }

        with patch('ai_slop_gate.providers.llm.groq.requests.post') as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = Mock()

            result = groq_provider.analyze("test code", input_file="test.py")

            assert len(result.observations) == 2
            assert result.observations[0].signal == "placeholder_one"
            assert result.observations[1].signal == "placeholder_two"


class TestGroqRetryLogic:
    """Test retry logic and strict JSON fallback."""

    def test_groq_retry_on_parse_error(self, groq_provider):
        """Test retry logic when first attempt fails JSON parsing."""
        invalid_json_response = {
            'choices': [{'message': {'content': 'not valid json {{{['}}]
        }
        valid_json_response = {
            'choices': [
                {
                    'message': {
                        'content': json.dumps([
                            {
                                'category': 'quality',
                                'signal': 'test',
                                'confidence': 0.7,
                                'severity': 'medium',
                                'message': 'Test issue',
                                'line': 1
                            }
                        ])
                    }
                }
            ]
        }

        with patch('ai_slop_gate.providers.llm.groq.requests.post') as mock_post:
            with patch('ai_slop_gate.providers.llm.groq.time.sleep'):
                # First call fails, second succeeds
                mock_post.side_effect = [
                    MagicMock(json=lambda: invalid_json_response, raise_for_status=Mock()),
                    MagicMock(json=lambda: valid_json_response, raise_for_status=Mock())
                ]

                result = groq_provider.analyze("test code", input_file="test.py")

                # Should succeed on second attempt
                assert len(result.observations) == 1
                assert result.observations[0].signal == "test"
                # Should have called API twice
                assert mock_post.call_count == 2

    def test_groq_retry_with_strict_json_on_second_attempt(self, groq_provider):
        """Test that second retry uses strict JSON mode."""
        valid_json_response = {
            'choices': [
                {
                    'message': {
                        'content': json.dumps([
                            {
                                'category': 'quality',
                                'signal': 'test',
                                'confidence': 0.7,
                                'severity': 'medium',
                                'message': 'Test issue',
                                'line': 1
                            }
                        ])
                    }
                }
            ]
        }

        with patch('ai_slop_gate.providers.llm.groq.requests.post') as mock_post:
            with patch('ai_slop_gate.providers.llm.groq.time.sleep'):
                mock_post.side_effect = [
                    MagicMock(json=lambda: {'choices': [{'message': {'content': 'bad'}}]}, raise_for_status=Mock()),
                    MagicMock(json=lambda: valid_json_response, raise_for_status=Mock())
                ]

                result = groq_provider.analyze("test code", input_file="test.py")

                assert len(result.observations) == 1
                
                # Check that second call included strict JSON mode
                second_call_args = mock_post.call_args_list[1]
                call_data = second_call_args[1]['json']
                assert call_data.get('response_format', {}).get('type') == 'json_object'

    def test_groq_max_retries_exhausted(self, groq_provider):
        """Test handling when max retries are exhausted."""
        invalid_json_response = {
            'choices': [{'message': {'content': 'invalid'}}]
        }

        with patch('ai_slop_gate.providers.llm.groq.requests.post') as mock_post:
            with patch('ai_slop_gate.providers.llm.groq.time.sleep'):
                mock_post.return_value.json.return_value = invalid_json_response
                mock_post.return_value.raise_for_status = Mock()

                result = groq_provider.analyze("test code", input_file="test.py")

                # Should return error on final failure
                assert result.observations == []
                assert "Error:" in result.raw_text or "Max retries" in result.raw_text


class TestGroqObservationSchema:
    """Test that observations match expected schema."""

    def test_groq_observation_has_required_fields(self, groq_provider):
        """Test that all observations have required fields."""
        mock_response = {
            'choices': [
                {
                    'message': {
                        'content': json.dumps([
                            {
                                'category': 'quality',
                                'signal': 'test_signal',
                                'confidence': 0.85,
                                'severity': 'medium',
                                'message': 'Test message',
                                'line': 42
                            }
                        ])
                    }
                }
            ]
        }

        with patch('ai_slop_gate.providers.llm.groq.requests.post') as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = Mock()

            result = groq_provider.analyze("test code", input_file="test.py")

            assert len(result.observations) == 1
            obs = result.observations[0]

            # Check required fields from make_observation
            assert hasattr(obs, 'category')
            assert hasattr(obs, 'signal')
            assert hasattr(obs, 'confidence')
            assert hasattr(obs, 'severity')
            assert hasattr(obs, 'message')
            assert hasattr(obs, 'location')
            
            # Verify values
            assert obs.category == 'quality'
            assert obs.signal == 'test_signal'
            assert obs.confidence == 0.85
            assert obs.severity == 'medium'
            assert obs.message == 'Test message'
            assert obs.location.line == 42

    def test_groq_observation_binds_to_input_file(self, groq_provider):
        """Test that observations are bound to input_file, not model's file field."""
        mock_response = {
            'choices': [
                {
                    'message': {
                        'content': json.dumps([
                            {
                                'category': 'quality',
                                'signal': 'test',
                                'confidence': 0.7,
                                'severity': 'medium',
                                'message': 'Test',
                                'line': 10,
                                'file': '/some/other/path.py'  # Should be ignored
                            }
                        ])
                    }
                }
            ]
        }

        with patch('ai_slop_gate.providers.llm.groq.requests.post') as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = Mock()

            result = groq_provider.analyze("test code", input_file="actual_file.py")

            obs = result.observations[0]
            # Should use input_file, not the file from response
            assert obs.location.file == "actual_file.py"

    def test_groq_observation_default_values(self, groq_provider):
        """Test that missing fields get sensible defaults."""
        mock_response = {
            'choices': [
                {
                    'message': {
                        'content': json.dumps([
                            {
                                'message': 'Only message provided'
                                # Missing: category, signal, confidence, severity, line
                            }
                        ])
                    }
                }
            ]
        }

        with patch('ai_slop_gate.providers.llm.groq.requests.post') as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = Mock()

            result = groq_provider.analyze("test code", input_file="test.py")

            obs = result.observations[0]
            assert obs.category == 'quality'  # default
            assert obs.signal == 'slop_detected'  # default
            assert obs.confidence == 0.7  # default
            assert obs.severity == 'medium'  # default
            assert obs.location.line == 1  # default


class TestGroqErrorHandling:
    """Test error handling in Groq provider."""

    def test_groq_api_timeout(self, groq_provider):
        """Test handling of API timeout."""
        with patch('ai_slop_gate.providers.llm.groq.requests.post') as mock_post:
            with patch('ai_slop_gate.providers.llm.groq.time.sleep'):
                mock_post.side_effect = [
                    Exception("Request timeout"),
                    Exception("Request timeout")
                ]

                result = groq_provider.analyze("test code", input_file="test.py")

                assert result.observations == []
                assert "Error:" in result.raw_text

    def test_groq_malformed_response(self, groq_provider):
        """Test handling of malformed API response."""
        malformed_response = {
            'choices': []  # Empty choices
        }

        with patch('ai_slop_gate.providers.llm.groq.requests.post') as mock_post:
            with patch('ai_slop_gate.providers.llm.groq.time.sleep'):
                # Both attempts return malformed
                mock_post.side_effect = [
                    MagicMock(json=lambda: malformed_response, raise_for_status=Mock()),
                    MagicMock(json=lambda: malformed_response, raise_for_status=Mock())
                ]

                result = groq_provider.analyze("test code", input_file="test.py")

                assert result.observations == []
                assert result.raw_text != ""
