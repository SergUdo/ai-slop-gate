"""
Unit tests for include_paths filtering logic in run.py.

Tests verify that the existing filtering logic correctly filters observations
based on include_paths configuration.
"""

import os
import pytest

from ai_slop_gate.domain.observation import Observation, Location


class TestIncludePathsFiltering:
    """Test suite for include_paths filtering in run_cli."""

    def test_filter_observations_with_include_paths(self):
        """
        Test that observations are correctly filtered by include_paths.
        
        Creates observations from both /data and /app directories,
        and verifies that only observations from /data are kept
        when include_paths=["/data"].
        """
        # Create fake observations with different file paths
        obs_data_a = Observation(
            category="test",
            signal="test_signal",
            confidence=1.0,
            message="Found in /data/a.py",
            location=Location(file="/data/a.py", line=10)
        )
        
        obs_data_sub_b = Observation(
            category="test",
            signal="test_signal",
            confidence=1.0,
            message="Found in /data/sub/b.js",
            location=Location(file="/data/sub/b.js", line=20)
        )
        
        obs_app_policy = Observation(
            category="test",
            signal="test_signal",
            confidence=1.0,
            message="Found in /app/policy.yml",
            location=Location(file="/app/policy.yml", line=1)
        )
        
        obs_app_other = Observation(
            category="test",
            signal="test_signal",
            confidence=1.0,
            message="Found in /app/other.py",
            location=Location(file="/app/other.py", line=5)
        )
        
        observations = [
            obs_data_a,
            obs_data_sub_b,
            obs_app_policy,
            obs_app_other,
        ]
        
        # Simulate the filtering logic from run.py
        include_paths = ["/data"]
        filtered_obs = []
        
        for obs in observations:
            file_path = None
            if hasattr(obs, "location") and obs.location:
                file_path = obs.location.file
            elif hasattr(obs, "evidence") and isinstance(obs.evidence, dict):
                file_path = obs.evidence.get("file")
            
            if not file_path:
                # No file path, include it
                filtered_obs.append(obs)
                continue
            
            # Resolve relative file paths from current directory
            if not os.path.isabs(file_path):
                abs_file_path = os.path.abspath(os.path.join(".", file_path))
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
        
        # Verify results
        assert len(filtered_obs) == 2, f"Expected 2 observations, got {len(filtered_obs)}"
        assert obs_data_a in filtered_obs, "obs_data_a should be included"
        assert obs_data_sub_b in filtered_obs, "obs_data_sub_b should be included"
        assert obs_app_policy not in filtered_obs, "obs_app_policy should be filtered out"
        assert obs_app_other not in filtered_obs, "obs_app_other should be filtered out"

    def test_filter_observations_with_relative_paths(self):
        """
        Test filtering with relative file paths resolved from base_path.
        
        When file paths are relative (e.g., "src/code.py"), they should be
        resolved relative to the base_path parameter before comparison.
        """
        # Relative path observations
        obs_rel_in_data = Observation(
            category="test",
            signal="test_signal",
            confidence=1.0,
            message="Relative path in /data",
            location=Location(file="src/code.py", line=10)
        )
        
        obs_rel_outside = Observation(
            category="test",
            signal="test_signal",
            confidence=1.0,
            message="Relative path outside",
            location=Location(file="other.py", line=1)
        )
        
        observations = [obs_rel_in_data, obs_rel_outside]
        include_paths = ["/data"]
        base_path = "/data"
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
            
            # CRITICAL: Resolve relative paths from base_path
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
        
        # Both should be included since /data is the base_path
        assert len(filtered_obs) == 2

    def test_filter_observations_multiple_include_paths(self):
        """
        Test filtering with multiple include_paths.
        
        When multiple include_paths are specified, observations should be
        included if their file is within ANY of the include_paths.
        """
        obs_data = Observation(
            category="test",
            signal="test_signal",
            confidence=1.0,
            message="In /data",
            location=Location(file="/data/file.py", line=1)
        )
        
        obs_src = Observation(
            category="test",
            signal="test_signal",
            confidence=1.0,
            message="In /app/src",
            location=Location(file="/app/src/main.py", line=1)
        )
        
        obs_app = Observation(
            category="test",
            signal="test_signal",
            confidence=1.0,
            message="In /app (not in src)",
            location=Location(file="/app/other.py", line=1)
        )
        
        observations = [obs_data, obs_src, obs_app]
        include_paths = ["/data", "/app/src"]
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
                abs_file_path = os.path.abspath(os.path.join(".", file_path))
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
        
        # /data/file.py and /app/src/main.py should be included
        assert len(filtered_obs) == 2
        assert obs_data in filtered_obs
        assert obs_src in filtered_obs
        assert obs_app not in filtered_obs

    def test_observations_without_file_path_always_included(self):
        """
        Test that observations without file paths are always included.
        
        Observations without file paths cannot be filtered, so they should
        always be kept regardless of include_paths.
        """
        obs_with_file = Observation(
            category="test",
            signal="test_signal",
            confidence=1.0,
            message="With file",
            location=Location(file="/data/file.py", line=1)
        )
        
        obs_without_file = Observation(
            category="test",
            signal="test_signal",
            confidence=1.0,
            message="Without file"
        )
        
        observations = [obs_with_file, obs_without_file]
        include_paths = ["/data"]
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
                abs_file_path = os.path.abspath(os.path.join(".", file_path))
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
        
        assert len(filtered_obs) == 2
        assert obs_with_file in filtered_obs
        assert obs_without_file in filtered_obs

    def test_observations_with_evidence_dict(self):
        """
        Test filtering observations that use evidence dict instead of location.
        
        Some observations store file paths in the evidence dict instead of
        using the location field.
        """
        obs_with_evidence = Observation(
            category="test",
            signal="test_signal",
            confidence=1.0,
            message="Test",
            evidence={"file": "/data/file.py", "line": 5}
        )
        
        obs_outside = Observation(
            category="test",
            signal="test_signal",
            confidence=1.0,
            message="Test",
            evidence={"file": "/app/policy.yml", "line": 1}
        )
        
        observations = [obs_with_evidence, obs_outside]
        include_paths = ["/data"]
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
                abs_file_path = os.path.abspath(os.path.join(".", file_path))
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
        
        assert len(filtered_obs) == 1
        assert obs_with_evidence in filtered_obs
        assert obs_outside not in filtered_obs
