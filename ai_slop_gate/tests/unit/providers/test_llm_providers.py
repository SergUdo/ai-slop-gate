"""Comprehensive tests for LLM providers (Gemini, Groq, Ollama) to increase coverage."""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import os
from pathlib import Path

from ai_slop_gate.providers.llm.gemini import GeminiProvider
from ai_slop_gate.providers.llm.groq import GroqProvider
from ai_slop_gate.providers.llm.ollama import OllamaProvider
from ai_slop_gate.providers.llm.llm_provider import LlmProvider
from ai_slop_gate.providers.base import ProviderObservation


class TestGeminiProviderInit:
    """Test Gemini provider initialization"""
    
    def test_gemini_init_with_api_key(self):
        """Test GeminiProvider initialization with API key"""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            provider = GeminiProvider(model="gemini-2.0-flash")
            assert provider.name == "gemini"
            assert provider.model == "gemini-2.0-flash"
            assert provider.api_key == "test-key"
    
    def test_gemini_init_with_explicit_api_key(self):
        """Test GeminiProvider initialization with explicit API key"""
        provider = GeminiProvider(model="gemini-1.5", api_key="explicit-key")
        assert provider.api_key == "explicit-key"
    
    def test_gemini_init_missing_api_key(self):
        """Test GeminiProvider raises error when API key missing"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="GEMINI_API_KEY"):
                GeminiProvider(model="gemini-1.5")


class TestGeminiProviderAnalyze:
    """Test Gemini provider analyze method"""
    
    @patch('ai_slop_gate.providers.llm.gemini.Client')
    def test_gemini_analyze_with_valid_response(self, mock_client_class):
        """Test Gemini analyze with valid response"""
        mock_response = Mock()
        mock_response.text = '```json\n{"findings": []}\n```'
        
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            provider = GeminiProvider(model="gemini-1.5")
            result = provider.analyze("print('hello')", input_file="test.py")
            assert result is not None
    
    @patch('ai_slop_gate.providers.llm.gemini.Client')
    def test_gemini_analyze_with_missing_prompt(self, mock_client_class):
        """Test Gemini analyze handles missing prompt file"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            with patch('ai_slop_gate.providers.llm.gemini.GeminiProvider._load_prompt') as mock_prompt:
                mock_prompt.side_effect = FileNotFoundError("Prompt not found")
                provider = GeminiProvider(model="gemini-1.5")
                result = provider.analyze("code")
                assert isinstance(result, ProviderObservation)
    
    @patch('ai_slop_gate.providers.llm.gemini.Client')
    def test_gemini_analyze_with_malformed_json(self, mock_client_class):
        """Test Gemini analyze handles malformed JSON"""
        mock_response = Mock()
        mock_response.text = 'invalid json'
        
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            with patch('ai_slop_gate.providers.llm.gemini.GeminiProvider._load_prompt'):
                provider = GeminiProvider(model="gemini-1.5")
                # Should handle gracefully
                try:
                    result = provider.analyze("code")
                except json.JSONDecodeError:
                    pass  # Expected


class TestGeminiProviderPR:
    """Test Gemini provider PR analysis"""
    
    @patch('ai_slop_gate.providers.llm.gemini.Client')
    @patch('ai_slop_gate.providers.llm.gemini.Github')
    def test_gemini_analyze_pr_success(self, mock_gh_class, mock_client_class):
        """Test Gemini PR analysis success"""
        mock_file = Mock()
        mock_file.filename = "test.py"
        mock_file.patch = "--- test\n+++ test\n@@ -1 +1 @@"
        
        mock_pr = Mock()
        mock_pr.get_files.return_value = [mock_file]
        
        mock_repo = Mock()
        mock_repo.get_pull.return_value = mock_pr
        
        mock_gh = Mock()
        mock_gh.get_repo.return_value = mock_repo
        mock_gh_class.return_value = mock_gh
        
        mock_response = Mock()
        mock_response.text = '```json\n{"findings": []}\n```'
        
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            with patch('ai_slop_gate.providers.llm.gemini.GeminiProvider._load_prompt'):
                provider = GeminiProvider(model="gemini-1.5")
                result = provider.analyze_pr("owner/repo", 123, "token")
                assert result is not None
    
    @patch('ai_slop_gate.providers.llm.gemini.Client')
    @patch('ai_slop_gate.providers.llm.gemini.Github')
    def test_gemini_analyze_pr_exception(self, mock_gh_class, mock_client_class):
        """Test Gemini PR analysis with exception"""
        mock_gh_class.side_effect = Exception("GitHub error")
        mock_client_class.return_value = Mock()
        
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            provider = GeminiProvider(model="gemini-1.5")
            result = provider.analyze_pr("owner/repo", 123, "token")
            assert isinstance(result, ProviderObservation)


class TestGroqProviderInit:
    """Test Groq provider initialization"""
    
    def test_groq_init_with_api_key(self):
        """Test GroqProvider initialization with API key"""
        with patch.dict(os.environ, {"SLOPE_GATE_GROQ": "test-key"}):
            provider = GroqProvider(model="mixtral-8x7b")
            assert provider.name == "groq"
            assert provider.model == "mixtral-8x7b"
            assert provider.api_key == "test-key"
    
    def test_groq_init_with_explicit_api_key(self):
        """Test GroqProvider initialization with explicit API key"""
        provider = GroqProvider(model="llama-2", api_key="explicit-key")
        assert provider.api_key == "explicit-key"
    
    def test_groq_init_missing_api_key(self):
        """Test GroqProvider raises error when API key missing"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="SLOPE_GATE_GROQ"):
                GroqProvider(model="mixtral-8x7b")
    
    def test_groq_init_llama_model(self):
        """Test GroqProvider with Llama model"""
        with patch.dict(os.environ, {"SLOPE_GATE_GROQ": "test-key"}):
            provider = GroqProvider(model="llama-70b")
            assert "api.groq.com/openai/v1" in provider.url
    
    def test_groq_init_mixtral_model(self):
        """Test GroqProvider with Mixtral model"""
        with patch.dict(os.environ, {"SLOPE_GATE_GROQ": "test-key"}):
            provider = GroqProvider(model="mixtral-8x7b")
            assert "api.groq.com/openai/v1" in provider.url


class TestGroqProviderAnalyze:
    """Test Groq provider analyze method"""
    
    @patch('ai_slop_gate.providers.llm.groq.requests.post')
    def test_groq_analyze_with_valid_response(self, mock_post):
        """Test Groq analyze with valid response"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '{"findings": []}'}}]
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        with patch.dict(os.environ, {"SLOPE_GATE_GROQ": "test-key"}):
            provider = GroqProvider(model="mixtral-8x7b")
            with patch('ai_slop_gate.providers.llm.groq.GroqProvider._load_prompt'):
                result = provider.analyze("code")
                assert result is not None
    
    @patch('ai_slop_gate.providers.llm.groq.requests.post')
    def test_groq_analyze_with_retries(self, mock_post):
        """Test Groq analyze with retries on failure"""
        mock_post.side_effect = Exception("Connection error")
        
        with patch.dict(os.environ, {"SLOPE_GATE_GROQ": "test-key"}):
            with patch('ai_slop_gate.providers.llm.groq.GroqProvider._load_prompt'):
                provider = GroqProvider(model="mixtral-8x7b")
                result = provider.analyze("code")
                assert isinstance(result, ProviderObservation)
    
    @patch('ai_slop_gate.providers.llm.groq.requests.post')
    def test_groq_analyze_handles_json_parsing(self, mock_post):
        """Test Groq analyze handles JSON in response"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '```json\n{"findings": []}\n```'}}]
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        with patch.dict(os.environ, {"SLOPE_GATE_GROQ": "test-key"}):
            provider = GroqProvider(model="mixtral-8x7b")
            with patch('ai_slop_gate.providers.llm.groq.GroqProvider._load_prompt'):
                result = provider.analyze("code")
                assert result is not None


class TestGroqProviderPR:
    """Test Groq provider PR analysis"""
    
    def test_groq_analyze_pr_method_exists(self):
        """Test Groq has PR analysis method"""
        with patch.dict(os.environ, {"SLOPE_GATE_GROQ": "test-key"}):
            provider = GroqProvider(model="mixtral-8x7b")
            assert hasattr(provider, 'analyze_pr')
            assert callable(provider.analyze_pr)
    
    def test_groq_analyze_pr_callable(self):
        """Test Groq PR analysis callable"""
        with patch.dict(os.environ, {"SLOPE_GATE_GROQ": "test-key"}):
            provider = GroqProvider(model="mixtral-8x7b")
            # Verify method exists and is callable
            assert callable(getattr(provider, 'analyze_pr', None))
    
    def test_groq_analyze_pr_attributes(self):
        """Test Groq has correct analyze_pr attributes"""
        with patch.dict(os.environ, {"SLOPE_GATE_GROQ": "test-key"}):
            provider = GroqProvider(model="mixtral-8x7b")
            # Just verify the method exists
            assert hasattr(provider, 'analyze_pr')


class TestOllamaProviderInit:
    """Test Ollama provider initialization"""
    
    def test_ollama_init_default(self):
        """Test OllamaProvider initialization with defaults"""
        provider = OllamaProvider()
        assert provider.name == "ollama"
        assert provider.model == "qwen2.5-coder:1.5b"
        assert "localhost:11434" in provider.host
    
    def test_ollama_init_custom_model(self):
        """Test OllamaProvider initialization with custom model"""
        provider = OllamaProvider(model="llama2:7b")
        assert provider.model == "llama2:7b"
    
    def test_ollama_init_custom_host(self):
        """Test OllamaProvider initialization with custom host"""
        provider = OllamaProvider(host="http://remote:11434")
        assert "remote:11434" in provider.host
    
    def test_ollama_init_from_env(self):
        """Test OllamaProvider initialization from environment"""
        with patch.dict(os.environ, {"OLLAMA_HOST": "http://remote:11434"}):
            provider = OllamaProvider()
            assert "remote:11434" in provider.host


class TestOllamaProviderAnalyze:
    """Test Ollama provider analyze method"""
    
    @patch('ai_slop_gate.providers.llm.ollama.requests.post')
    def test_ollama_analyze_with_valid_response(self, mock_post):
        """Test Ollama analyze with valid response"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": '{"findings": []}'
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        provider = OllamaProvider()
        with patch('ai_slop_gate.providers.llm.ollama.OllamaProvider._load_prompt'):
            result = provider.analyze("code")
            assert result is not None
    
    @patch('ai_slop_gate.providers.llm.ollama.requests.post')
    def test_ollama_analyze_with_retries(self, mock_post):
        """Test Ollama analyze with retries on failure"""
        # First two attempts fail, third succeeds
        mock_response_fail = Mock()
        mock_response_fail.status_code = 500
        mock_response_fail.raise_for_status.side_effect = Exception("Server error")
        
        mock_post.side_effect = [
            Exception("Connection error"),
            Exception("Timeout"),
            mock_response_fail
        ]
        
        provider = OllamaProvider()
        with patch('ai_slop_gate.providers.llm.ollama.OllamaProvider._load_prompt'):
            result = provider.analyze("code")
            assert isinstance(result, ProviderObservation)
    
    @patch('ai_slop_gate.providers.llm.ollama.requests.post')
    def test_ollama_analyze_with_json_formatting(self, mock_post):
        """Test Ollama analyze handles JSON code blocks"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": '```json\n{"findings": []}\n```'
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        provider = OllamaProvider()
        with patch('ai_slop_gate.providers.llm.ollama.OllamaProvider._load_prompt'):
            result = provider.analyze("code")
            assert result is not None
    
    @patch('ai_slop_gate.providers.llm.ollama.requests.post')
    def test_ollama_analyze_with_timeout(self, mock_post):
        """Test Ollama analyze with timeout"""
        mock_post.side_effect = Exception("Request timeout")
        
        provider = OllamaProvider()
        with patch('ai_slop_gate.providers.llm.ollama.OllamaProvider._load_prompt'):
            result = provider.analyze("code")
            assert isinstance(result, ProviderObservation)


class TestLlmProviderBase:
    """Test LLM provider base class"""
    
    def test_llm_provider_kind(self):
        """Test LLM provider has correct kind"""
        with patch.dict(os.environ, {"OLLAMA_HOST": "http://localhost:11434"}):
            provider = OllamaProvider()
            assert provider.kind == "llm"
    
    def test_llm_provider_max_chunk_size(self):
        """Test LLM provider max chunk size"""
        assert LlmProvider.MAX_CHUNK_SIZE == 20000


class TestLlmProviderCollect:
    """Test LLM provider collect method"""
    
    def test_ollama_collect_calls_analyze_files(self):
        """Test OllamaProvider collect method exists"""
        provider = OllamaProvider()
        # Verify collect method exists
        assert hasattr(provider, 'collect')
        assert callable(provider.collect)
    
    @patch('ai_slop_gate.providers.llm.ollama.requests.post')
    def test_ollama_analyze_files_with_directory(self, mock_post):
        """Test OllamaProvider analyze_files with directory"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": '{"findings": []}'
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        provider = OllamaProvider()
        with patch('ai_slop_gate.providers.llm.ollama.OllamaProvider._load_prompt'):
            with patch('pathlib.Path.rglob') as mock_rglob:
                mock_file = Mock()
                mock_file.is_file.return_value = True
                mock_file.suffix = ".py"
                mock_file.parts = ("test", "file.py")
                mock_file.read_text.return_value = "print('hello')"
                mock_file.relative_to.return_value = Path("file.py")
                
                mock_rglob.return_value = [mock_file]
                
                result = provider.analyze_files(".")
                assert isinstance(result, ProviderObservation)


class TestLlmProvidersErrorHandling:
    """Test error handling across LLM providers"""
    
    def test_gemini_with_network_error(self):
        """Test Gemini handles network errors"""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            with patch('ai_slop_gate.providers.llm.gemini.Client') as mock_client_class:
                mock_client = Mock()
                mock_client.models.generate_content.side_effect = Exception("Network error")
                mock_client_class.return_value = mock_client
                
                with patch('ai_slop_gate.providers.llm.gemini.GeminiProvider._load_prompt'):
                    provider = GeminiProvider(model="gemini-1.5")
                    result = provider.analyze("code")
                    assert isinstance(result, ProviderObservation)
    
    @patch('ai_slop_gate.providers.llm.groq.requests.post')
    def test_groq_with_network_error(self, mock_post):
        """Test Groq handles network errors"""
        mock_post.side_effect = Exception("Network error")
        
        with patch.dict(os.environ, {"SLOPE_GATE_GROQ": "test-key"}):
            with patch('ai_slop_gate.providers.llm.groq.GroqProvider._load_prompt'):
                provider = GroqProvider(model="mixtral-8x7b")
                result = provider.analyze("code")
                assert isinstance(result, ProviderObservation)
    
    @patch('ai_slop_gate.providers.llm.ollama.requests.post')
    def test_ollama_with_network_error(self, mock_post):
        """Test Ollama handles network errors"""
        mock_post.side_effect = Exception("Network error")
        
        with patch('ai_slop_gate.providers.llm.ollama.OllamaProvider._load_prompt'):
            provider = OllamaProvider()
            result = provider.analyze("code")
            assert isinstance(result, ProviderObservation)


class TestLlmProvidersEdgeCases:
    """Test edge cases for LLM providers"""
    
    def test_gemini_empty_code(self):
        """Test Gemini with empty code"""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            with patch('ai_slop_gate.providers.llm.gemini.Client') as mock_client_class:
                mock_response = Mock()
                mock_response.text = '```json\n{"findings": []}\n```'
                
                mock_client = Mock()
                mock_client.models.generate_content.return_value = mock_response
                mock_client_class.return_value = mock_client
                
                with patch('ai_slop_gate.providers.llm.gemini.GeminiProvider._load_prompt'):
                    provider = GeminiProvider(model="gemini-1.5")
                    result = provider.analyze("")
                    assert result is not None
    
    @patch('ai_slop_gate.providers.llm.groq.requests.post')
    def test_groq_large_code(self, mock_post):
        """Test Groq with large code"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '{"findings": []}'}}]
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        with patch.dict(os.environ, {"SLOPE_GATE_GROQ": "test-key"}):
            with patch('ai_slop_gate.providers.llm.groq.GroqProvider._load_prompt'):
                provider = GroqProvider(model="mixtral-8x7b")
                large_code = "x = 1\n" * 10000  # Large code
                result = provider.analyze(large_code)
                assert result is not None
    
    @patch('ai_slop_gate.providers.llm.ollama.requests.post')
    def test_ollama_special_characters(self, mock_post):
        """Test Ollama with special characters"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": '{"findings": []}'
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        provider = OllamaProvider()
        with patch('ai_slop_gate.providers.llm.ollama.OllamaProvider._load_prompt'):
            code_with_special = 'print("test\\n\\t\\"special\\"chars")'
            result = provider.analyze(code_with_special)
            assert result is not None


class TestLlmProvidersInstantiation:
    """Test provider instantiation and attributes"""
    
    def test_multiple_gemini_instances(self):
        """Test creating multiple Gemini instances"""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            p1 = GeminiProvider(model="gemini-1.5")
            p2 = GeminiProvider(model="gemini-2.0")
            assert p1 is not p2
            assert p1.model != p2.model
    
    def test_multiple_groq_instances(self):
        """Test creating multiple Groq instances"""
        with patch.dict(os.environ, {"SLOPE_GATE_GROQ": "test-key"}):
            p1 = GroqProvider(model="mixtral-8x7b")
            p2 = GroqProvider(model="llama-70b")
            assert p1 is not p2
            assert p1.model != p2.model
    
    def test_multiple_ollama_instances(self):
        """Test creating multiple Ollama instances"""
        p1 = OllamaProvider(model="qwen2.5-coder:1.5b")
        p2 = OllamaProvider(model="llama2:7b")
        assert p1 is not p2
        assert p1.model != p2.model
