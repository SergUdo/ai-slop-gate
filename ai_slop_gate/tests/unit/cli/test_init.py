import os
import yaml
from pathlib import Path
from ai_slop_gate.cli.init import run_init

def test_init_creates_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    run_init(force=False)

    config = Path(".ai-slop-gate.yml")
    assert config.exists()

    data = yaml.safe_load(config.read_text())
    assert data["version"] == 1
    assert data["mode"] == "advisory"

def test_init_refuses_overwrite(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    Path(".ai-slop-gate.yml").write_text("test")

    try:
        run_init(force=False)
        assert False, "Expected SystemExit"
    except SystemExit:
        pass

def test_init_force_overwrites(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    Path(".ai-slop-gate.yml").write_text("old")
    run_init(force=True)

    data = yaml.safe_load(Path(".ai-slop-gate.yml").read_text())
    print(data)
    assert "providers" in data
