import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import yaml
from ai_slop_gate.cli.init import run_init


class TestRunInit:
    """Test suite for run_init function."""

    def test_init_creates_default_config(self, tmp_path, monkeypatch):
        """Test that run_init creates .ai-slop-gate.yml file."""
        monkeypatch.chdir(tmp_path)
        
        run_init(force=False)
        
        config_path = Path(".ai-slop-gate.yml")
        assert config_path.exists()

    def test_init_creates_file_with_version(self, tmp_path, monkeypatch):
        """Test that created config contains version field."""
        monkeypatch.chdir(tmp_path)
        
        run_init(force=False)
        
        config_path = Path(".ai-slop-gate.yml")
        data = yaml.safe_load(config_path.read_text())
        assert "version" in data
        assert data["version"] == 1

    def test_init_creates_file_with_mode(self, tmp_path, monkeypatch):
        """Test that created config contains mode field."""
        monkeypatch.chdir(tmp_path)
        
        run_init(force=False)
        
        config_path = Path(".ai-slop-gate.yml")
        data = yaml.safe_load(config_path.read_text())
        assert "mode" in data
        assert data["mode"] == "advisory"

    def test_init_creates_file_with_providers(self, tmp_path, monkeypatch):
        """Test that created config contains providers field."""
        monkeypatch.chdir(tmp_path)
        
        run_init(force=False)
        
        config_path = Path(".ai-slop-gate.yml")
        data = yaml.safe_load(config_path.read_text())
        assert "providers" in data
        assert isinstance(data["providers"], list)
        assert len(data["providers"]) > 0

    def test_init_creates_file_with_compliance(self, tmp_path, monkeypatch):
        """Test that created config contains compliance section."""
        monkeypatch.chdir(tmp_path)
        
        run_init(force=False)
        
        config_path = Path(".ai-slop-gate.yml")
        data = yaml.safe_load(config_path.read_text())
        assert "compliance" in data
        assert isinstance(data["compliance"], dict)

    def test_init_creates_file_with_policy(self, tmp_path, monkeypatch):
        """Test that created config contains policy section."""
        monkeypatch.chdir(tmp_path)
        
        run_init(force=False)
        
        config_path = Path(".ai-slop-gate.yml")
        data = yaml.safe_load(config_path.read_text())
        assert "policy" in data
        assert isinstance(data["policy"], dict)

    def test_init_refuses_overwrite_without_force(self, tmp_path, monkeypatch):
        """Test that init refuses to overwrite existing file without --force."""
        monkeypatch.chdir(tmp_path)
        
        # Create an existing config
        config_path = Path(".ai-slop-gate.yml")
        config_path.write_text("existing: config")
        
        with pytest.raises(SystemExit):
            run_init(force=False)

    def test_init_overwrites_with_force(self, tmp_path, monkeypatch):
        """Test that init overwrites file with --force flag."""
        monkeypatch.chdir(tmp_path)
        
        # Create an existing config with different content
        config_path = Path(".ai-slop-gate.yml")
        config_path.write_text("old: content")
        
        run_init(force=True)
        
        # File should exist and have new content
        assert config_path.exists()
        data = yaml.safe_load(config_path.read_text())
        assert data.get("version") == 1
        assert "old" not in str(data)

    def test_init_default_config_structure(self, tmp_path, monkeypatch):
        """Test that created config has expected structure."""
        monkeypatch.chdir(tmp_path)
        
        run_init(force=False)
        
        config_path = Path(".ai-slop-gate.yml")
        data = yaml.safe_load(config_path.read_text())
        
        assert "version" in data
        assert "mode" in data
        assert "providers" in data
        assert "compliance" in data
        assert "policy" in data

    def test_init_compliance_has_enabled_field(self, tmp_path, monkeypatch):
        """Test that compliance config has enabled field."""
        monkeypatch.chdir(tmp_path)
        
        run_init(force=False)
        
        config_path = Path(".ai-slop-gate.yml")
        data = yaml.safe_load(config_path.read_text())
        
        compliance = data.get("compliance", {})
        assert "enabled" in compliance

    def test_init_compliance_has_profiles(self, tmp_path, monkeypatch):
        """Test that compliance config has profiles field."""
        monkeypatch.chdir(tmp_path)
        
        run_init(force=False)
        
        config_path = Path(".ai-slop-gate.yml")
        data = yaml.safe_load(config_path.read_text())
        
        compliance = data.get("compliance", {})
        assert "profiles" in compliance

    def test_init_compliance_has_forbid_licenses(self, tmp_path, monkeypatch):
        """Test that compliance config has forbid_licenses field."""
        monkeypatch.chdir(tmp_path)
        
        run_init(force=False)
        
        config_path = Path(".ai-slop-gate.yml")
        data = yaml.safe_load(config_path.read_text())
        
        compliance = data.get("compliance", {})
        assert "forbid_licenses" in compliance

    def test_init_policy_has_ruleset(self, tmp_path, monkeypatch):
        """Test that policy config has ruleset field."""
        monkeypatch.chdir(tmp_path)
        
        run_init(force=False)
        
        config_path = Path(".ai-slop-gate.yml")
        data = yaml.safe_load(config_path.read_text())
        
        policy = data.get("policy", {})
        assert "ruleset" in policy

    def test_init_force_false_default(self, tmp_path, monkeypatch):
        """Test init with force=False (default)."""
        monkeypatch.chdir(tmp_path)
        
        run_init()  # force defaults to False
        
        config_path = Path(".ai-slop-gate.yml")
        assert config_path.exists()

    def test_init_multiple_calls_with_force(self, tmp_path, monkeypatch):
        """Test multiple init calls with force flag."""
        monkeypatch.chdir(tmp_path)
        
        run_init(force=False)
        first_content = Path(".ai-slop-gate.yml").read_text()
        
        run_init(force=True)
        second_content = Path(".ai-slop-gate.yml").read_text()
        
        # Content should be the same (default config)
        assert first_content == second_content

    def test_init_providers_list_not_empty(self, tmp_path, monkeypatch):
        """Test that providers list is populated."""
        monkeypatch.chdir(tmp_path)
        
        run_init(force=False)
        
        config_path = Path(".ai-slop-gate.yml")
        data = yaml.safe_load(config_path.read_text())
        
        providers = data.get("providers", [])
        assert len(providers) > 0
        assert "static" in providers

    def test_init_creates_valid_yaml(self, tmp_path, monkeypatch):
        """Test that created file is valid YAML."""
        monkeypatch.chdir(tmp_path)
        
        run_init(force=False)
        
        config_path = Path(".ai-slop-gate.yml")
        content = config_path.read_text()
        
        # Should not raise any exception
        data = yaml.safe_load(content)
        assert data is not None
        assert isinstance(data, dict)

    def test_init_file_is_readable_after_creation(self, tmp_path, monkeypatch):
        """Test that created file can be read."""
        monkeypatch.chdir(tmp_path)
        
        run_init(force=False)
        
        config_path = Path(".ai-slop-gate.yml")
        assert config_path.exists()
        assert config_path.is_file()
        assert len(config_path.read_text()) > 0

    def test_init_preserves_on_second_call_without_force(self, tmp_path, monkeypatch):
        """Test that second init call preserves file without force."""
        monkeypatch.chdir(tmp_path)
        
        run_init(force=False)
        first_content = Path(".ai-slop-gate.yml").read_text()
        
        # Second call should raise exception
        with pytest.raises(SystemExit):
            run_init(force=False)
        
        # File content should be unchanged
        second_content = Path(".ai-slop-gate.yml").read_text()
        assert first_content == second_content

    def test_init_compliance_disabled_by_default(self, tmp_path, monkeypatch):
        """Test that compliance is disabled by default."""
        monkeypatch.chdir(tmp_path)
        
        run_init(force=False)
        
        config_path = Path(".ai-slop-gate.yml")
        data = yaml.safe_load(config_path.read_text())
        
        compliance = data.get("compliance", {})
        assert compliance.get("enabled") is False

    def test_init_mode_is_advisory_by_default(self, tmp_path, monkeypatch):
        """Test that mode is advisory by default."""
        monkeypatch.chdir(tmp_path)
        
        run_init(force=False)
        
        config_path = Path(".ai-slop-gate.yml")
        data = yaml.safe_load(config_path.read_text())
        
        assert data.get("mode") == "advisory"
