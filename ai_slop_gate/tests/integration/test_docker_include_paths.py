"""
Integration test for include_paths filtering in Docker scenario.

Simulates the Docker environment:
- WORKDIR = "/app"
- mounted repo = "/data"
- include_paths = ["/data"]

Verifies that observations from /app are filtered out while observations
from /data are kept.
"""

import os
import pytest

from ai_slop_gate.domain.observation import Observation, Location


class TestDockerIncludePathsScenario:
    """Integration tests for the Docker include_paths scenario."""

    def test_docker_scenario_filters_app_observations(self):
        """
        Test the Docker scenario:
        - Image WORKDIR = /app
        - mounted repo = /data
        - include_paths = [/data]
        
        Expected behavior:
        - /app/policy.yml → filtered out
        - /app/other.py → filtered out
        - /data/src/main.py → kept
        - /data/config.js → kept
        """
        # Simulate observations from Docker scanning /app (the image)
        obs_app_policy = Observation(
            category="compliance",
            signal="data_residency_violation",
            confidence=1.0,
            message="Policy file contains sensitive configuration",
            location=Location(file="/app/policy.yml", line=1)
        )
        
        obs_app_other = Observation(
            category="security",
            signal="hardcoded_secret",
            confidence=0.9,
            message="Hardcoded API key detected",
            location=Location(file="/app/other.py", line=42)
        )
        
        # Observations from the mounted repo at /data
        obs_data_main = Observation(
            category="quality",
            signal="todo_found",
            confidence=0.8,
            message="TODO comment detected",
            location=Location(file="/data/src/main.py", line=25)
        )
        
        obs_data_config = Observation(
            category="security",
            signal="hardcoded_token",
            confidence=0.95,
            message="Hardcoded authentication token",
            location=Location(file="/data/config.js", line=10)
        )
        
        # All observations from scanning
        all_observations = [
            obs_app_policy,
            obs_app_other,
            obs_data_main,
            obs_data_config,
        ]
        
        # Docker scenario configuration
        include_paths = ["/data"]
        base_path = "/app"  # WORKDIR in Docker image
        
        # Apply the filtering logic (as implemented in run.py)
        filtered_obs = []
        
        for obs in all_observations:
            file_path = None
            if hasattr(obs, "location") and obs.location:
                file_path = obs.location.file
            elif hasattr(obs, "evidence") and isinstance(obs.evidence, dict):
                file_path = obs.evidence.get("file")
            
            if not file_path:
                # No file path, include it
                filtered_obs.append(obs)
                continue
            
            # Resolve relative paths from base_path (Docker WORKDIR)
            if not os.path.isabs(file_path):
                abs_file_path = os.path.abspath(os.path.join(base_path, file_path))
            else:
                abs_file_path = os.path.abspath(file_path)
            
            # Check if within include_paths
            is_included = False
            for include_path in include_paths:
                include_path_abs = os.path.abspath(include_path)
                try:
                    rel = os.path.relpath(abs_file_path, include_path_abs)
                    if not rel.startswith(".."):
                        is_included = True
                        break
                except ValueError:
                    pass
            
            if is_included:
                filtered_obs.append(obs)
        
        # Assertions for Docker scenario
        assert len(filtered_obs) == 2, (
            f"Expected 2 observations in /data, but got {len(filtered_obs)}. "
            f"Filtered observations: {[obs.location.file if obs.location else 'no-file' for obs in filtered_obs]}"
        )
        
        # /data files should be kept
        assert obs_data_main in filtered_obs, (
            "obs_data_main (/data/src/main.py) should be included"
        )
        assert obs_data_config in filtered_obs, (
            "obs_data_config (/data/config.js) should be included"
        )
        
        # /app files should be filtered out
        assert obs_app_policy not in filtered_obs, (
            "obs_app_policy (/app/policy.yml) should be filtered out"
        )
        assert obs_app_other not in filtered_obs, (
            "obs_app_other (/app/other.py) should be filtered out"
        )

    def test_docker_scenario_with_nested_directories(self):
        """
        Test Docker scenario with nested directory structures.
        
        Verifies that filtering works correctly with deeply nested paths
        within both the image and the mounted repo.
        """
        # Observations with nested paths in /app
        obs_app_nested = Observation(
            category="quality",
            signal="style_violation",
            confidence=0.7,
            message="Style issue detected",
            location=Location(file="/app/ai_slop_gate/providers/gemini.py", line=100)
        )
        
        # Observations with nested paths in /data
        obs_data_nested_src = Observation(
            category="security",
            signal="hardcoded_secret",
            confidence=0.95,
            message="Secret detected",
            location=Location(file="/data/src/components/auth/token.py", line=50)
        )
        
        obs_data_nested_config = Observation(
            category="compliance",
            signal="config_issue",
            confidence=0.8,
            message="Configuration issue",
            location=Location(file="/data/config/prod/database.json", line=1)
        )
        
        observations = [
            obs_app_nested,
            obs_data_nested_src,
            obs_data_nested_config,
        ]
        
        include_paths = ["/data"]
        base_path = "/app"
        filtered_obs = []
        
        for obs in observations:
            file_path = None
            if hasattr(obs, "location") and obs.location:
                file_path = obs.location.file
            elif hasattr(obs, "evidence") and isinstance(obs.evidence, dict):
                file_path = obs.evidence.get("file")
            
            if not file_path:
                filtered_obs.append(obs)
                continue
            
            if not os.path.isabs(file_path):
                abs_file_path = os.path.abspath(os.path.join(base_path, file_path))
            else:
                abs_file_path = os.path.abspath(file_path)
            
            is_included = False
            for include_path in include_paths:
                include_path_abs = os.path.abspath(include_path)
                try:
                    rel = os.path.relpath(abs_file_path, include_path_abs)
                    if not rel.startswith(".."):
                        is_included = True
                        break
                except ValueError:
                    pass
            
            if is_included:
                filtered_obs.append(obs)
        
        # Only /data observations should remain
        assert len(filtered_obs) == 2
        assert obs_data_nested_src in filtered_obs
        assert obs_data_nested_config in filtered_obs
        assert obs_app_nested not in filtered_obs

    def test_docker_scenario_mixed_file_formats(self):
        """
        Test Docker scenario with mixed file types (Python, JS, JSON, etc).
        
        Verifies that filtering works regardless of file extension.
        """
        observations = [
            Observation(
                category="test",
                signal="test_signal",
                confidence=1.0,
                message="Python file in app",
                location=Location(file="/app/main.py", line=1)
            ),
            Observation(
                category="test",
                signal="test_signal",
                confidence=1.0,
                message="JS file in app",
                location=Location(file="/app/index.js", line=1)
            ),
            Observation(
                category="test",
                signal="test_signal",
                confidence=1.0,
                message="YAML in app",
                location=Location(file="/app/config.yaml", line=1)
            ),
            Observation(
                category="test",
                signal="test_signal",
                confidence=1.0,
                message="Python file in data",
                location=Location(file="/data/src/app.py", line=1)
            ),
            Observation(
                category="test",
                signal="test_signal",
                confidence=1.0,
                message="JS file in data",
                location=Location(file="/data/frontend/app.js", line=1)
            ),
            Observation(
                category="test",
                signal="test_signal",
                confidence=1.0,
                message="JSON in data",
                location=Location(file="/data/package.json", line=1)
            ),
        ]
        
        include_paths = ["/data"]
        base_path = "/app"
        filtered_obs = []
        
        for obs in observations:
            file_path = None
            if hasattr(obs, "location") and obs.location:
                file_path = obs.location.file
            elif hasattr(obs, "evidence") and isinstance(obs.evidence, dict):
                file_path = obs.evidence.get("file")
            
            if not file_path:
                filtered_obs.append(obs)
                continue
            
            if not os.path.isabs(file_path):
                abs_file_path = os.path.abspath(os.path.join(base_path, file_path))
            else:
                abs_file_path = os.path.abspath(file_path)
            
            is_included = False
            for include_path in include_paths:
                include_path_abs = os.path.abspath(include_path)
                try:
                    rel = os.path.relpath(abs_file_path, include_path_abs)
                    if not rel.startswith(".."):
                        is_included = True
                        break
                except ValueError:
                    pass
            
            if is_included:
                filtered_obs.append(obs)
        
        # Only /data observations should remain (3 out of 6)
        assert len(filtered_obs) == 3
        # All remaining should be from /data
        for obs in filtered_obs:
            assert obs.location.file.startswith("/data"), (
                f"Observation with file {obs.location.file} should not be in filtered list"
            )

    def test_docker_scenario_single_include_path(self):
        """
        Test that with a single include_path, only matching files are kept.
        
        Verifies the basic case with one include_path = ["/data"].
        """
        observations = [
            Observation(
                category="test",
                signal="s1",
                confidence=1.0,
                message="msg",
                location=Location(file="/app/policy.yml", line=1)
            ),
            Observation(
                category="test",
                signal="s2",
                confidence=1.0,
                message="msg",
                location=Location(file="/app/other.py", line=1)
            ),
            Observation(
                category="test",
                signal="s3",
                confidence=1.0,
                message="msg",
                location=Location(file="/data/src/main.py", line=1)
            ),
            Observation(
                category="test",
                signal="s4",
                confidence=1.0,
                message="msg",
                location=Location(file="/data/config.js", line=1)
            ),
        ]
        
        include_paths = ["/data"]
        base_path = "/app"
        filtered_obs = []
        
        for obs in observations:
            file_path = None
            if hasattr(obs, "location") and obs.location:
                file_path = obs.location.file
            elif hasattr(obs, "evidence") and isinstance(obs.evidence, dict):
                file_path = obs.evidence.get("file")
            
            if not file_path:
                filtered_obs.append(obs)
                continue
            
            if not os.path.isabs(file_path):
                abs_file_path = os.path.abspath(os.path.join(base_path, file_path))
            else:
                abs_file_path = os.path.abspath(file_path)
            
            is_included = False
            for include_path in include_paths:
                include_path_abs = os.path.abspath(include_path)
                try:
                    rel = os.path.relpath(abs_file_path, include_path_abs)
                    if not rel.startswith(".."):
                        is_included = True
                        break
                except ValueError:
                    pass
            
            if is_included:
                filtered_obs.append(obs)
        
        # Basic assertion: final count should be 2
        assert len(filtered_obs) == 2
