import os
import yaml
import tempfile
import shutil
import pytest

from ai_slop_gate.reporters.stdout import run_init, CONFIG_FILE, DEFAULT_CONFIG


def test_run_init_creates_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run_init()
    p = tmp_path / CONFIG_FILE
    assert p.exists()
    data = yaml.safe_load(p.read_text())
    assert data["mode"] == DEFAULT_CONFIG["mode"]

def test_run_init_existing_no_force(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / CONFIG_FILE).write_text("x")
    with pytest.raises(SystemExit):
        run_init(force=False)
