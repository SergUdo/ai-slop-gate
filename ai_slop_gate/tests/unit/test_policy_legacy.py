"""Unit tests for policy_legacy module."""
import pytest
import tempfile
import os
import yaml
from ai_slop_gate.policy_legacy import load_policy


class TestLoadPolicy:
    """Test suite for load_policy function."""

    def test_load_policy_basic(self):
        """Test loading a basic policy file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            policy_dict = {
                'version': '1.0',
                'provider': 'static'
            }
            yaml.dump(policy_dict, f)
            f.flush()
            
            result = load_policy(f.name)
            assert result['version'] == '1.0'
            assert result['provider'] == 'static'
            
            os.unlink(f.name)

    def test_load_policy_with_rules(self):
        """Test loading policy with rules section."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            policy_dict = {
                'version': '1.0',
                'rules': [
                    {'name': 'rule1', 'enabled': True},
                    {'name': 'rule2', 'enabled': False}
                ]
            }
            yaml.dump(policy_dict, f)
            f.flush()
            
            result = load_policy(f.name)
            assert len(result['rules']) == 2
            assert result['rules'][0]['name'] == 'rule1'
            assert result['rules'][1]['name'] == 'rule2'
            
            os.unlink(f.name)

    def test_load_policy_nested_config(self):
        """Test loading policy with nested configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            policy_dict = {
                'version': '1.0',
                'compliance': {
                    'security_audit': {
                        'enforce_data_residency': 'EU',
                        'forbidden_licenses': ['GPL', 'AGPL']
                    }
                }
            }
            yaml.dump(policy_dict, f)
            f.flush()
            
            result = load_policy(f.name)
            assert result['compliance']['security_audit']['enforce_data_residency'] == 'EU'
            assert 'GPL' in result['compliance']['security_audit']['forbidden_licenses']
            
            os.unlink(f.name)

    def test_load_policy_with_provider_config(self):
        """Test loading policy with provider configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            policy_dict = {
                'provider': 'gemini',
                'model': 'gemini-2.5-flash'
            }
            yaml.dump(policy_dict, f)
            f.flush()
            
            result = load_policy(f.name)
            assert result['provider'] == 'gemini'
            assert result['model'] == 'gemini-2.5-flash'
            
            os.unlink(f.name)

    def test_load_policy_file_not_found(self):
        """Test loading policy from non-existent file."""
        with pytest.raises(FileNotFoundError):
            load_policy('/nonexistent/path/policy.yml')

    def test_load_policy_with_list_values(self):
        """Test loading policy with list values."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            policy_dict = {
                'providers': ['static', 'gemini', 'groq'],
                'checks': ['lint', 'security', 'compliance']
            }
            yaml.dump(policy_dict, f)
            f.flush()
            
            result = load_policy(f.name)
            assert isinstance(result['providers'], list)
            assert len(result['providers']) == 3
            assert 'gemini' in result['providers']
            
            os.unlink(f.name)

    def test_load_policy_with_string_values(self):
        """Test loading policy with string values."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            policy_dict = {
                'name': 'Enterprise Policy',
                'description': 'Policy for enterprise use'
            }
            yaml.dump(policy_dict, f)
            f.flush()
            
            result = load_policy(f.name)
            assert result['name'] == 'Enterprise Policy'
            assert result['description'] == 'Policy for enterprise use'
            
            os.unlink(f.name)

    def test_load_policy_with_boolean_values(self):
        """Test loading policy with boolean values."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            policy_dict = {
                'enabled': True,
                'verbose': False
            }
            yaml.dump(policy_dict, f)
            f.flush()
            
            result = load_policy(f.name)
            assert result['enabled'] is True
            assert result['verbose'] is False
            
            os.unlink(f.name)

    def test_load_policy_with_numeric_values(self):
        """Test loading policy with numeric values."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            policy_dict = {
                'threshold': 75,
                'timeout': 30.5
            }
            yaml.dump(policy_dict, f)
            f.flush()
            
            result = load_policy(f.name)
            assert result['threshold'] == 75
            assert result['timeout'] == 30.5
            
            os.unlink(f.name)

    def test_load_policy_empty_file(self):
        """Test loading an empty policy file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("")
            f.flush()
            
            result = load_policy(f.name)
            assert result is None
            
            os.unlink(f.name)

    def test_load_policy_encoding(self):
        """Test loading policy file with UTF-8 encoding."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False, encoding='utf-8') as f:
            policy_dict = {
                'description': 'Policy for ÜñíçödË test'
            }
            yaml.dump(policy_dict, f)
            f.flush()
            
            result = load_policy(f.name)
            assert 'description' in result
            
            os.unlink(f.name)

    def test_load_policy_returns_dict(self):
        """Test that load_policy returns a dictionary."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            policy_dict = {'key': 'value'}
            yaml.dump(policy_dict, f)
            f.flush()
            
            result = load_policy(f.name)
            assert isinstance(result, dict)
            
            os.unlink(f.name)

    def test_load_policy_preserves_structure(self):
        """Test that load_policy preserves nested structure."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            policy_dict = {
                'level1': {
                    'level2': {
                        'level3': 'value'
                    }
                }
            }
            yaml.dump(policy_dict, f)
            f.flush()
            
            result = load_policy(f.name)
            assert result['level1']['level2']['level3'] == 'value'
            
            os.unlink(f.name)
