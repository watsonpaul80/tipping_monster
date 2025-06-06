import sys
from pathlib import Path
import subprocess

sys.path.append(str(Path(__file__).resolve().parents[1]))

from tmcli import main


def test_pipeline_subcommand(monkeypatch):
    calls = []
    def fake_run(cmd, check=True, env=None):
        calls.append((cmd, env))
    monkeypatch.setattr(subprocess, "run", fake_run)
    main(["pipeline", "--date", "2025-06-07"])
    assert calls[0][0] == ["bash", "run_pipeline_with_venv.sh"]
    assert calls[0][1]["TM_DATE"] == "2025-06-07"


def test_roi_subcommand(monkeypatch):
    calls = []
    def fake_run(cmd, check=True, env=None):
        calls.append((cmd, env))
    monkeypatch.setattr(subprocess, "run", fake_run)
    main(["roi", "--date", "2025-06-07"])
    assert calls[0][0] == ["bash", "run_roi_pipeline.sh", "2025-06-07"]
    assert calls[0][1]["DATE"] == "2025-06-07"


def test_sniper_subcommand(monkeypatch):
    calls = []
    def fake_run(cmd, check=True, env=None):
        calls.append(cmd)
    monkeypatch.setattr(subprocess, "run", fake_run)
    main(["sniper"])
    assert calls[0] == ["bash", "generate_and_schedule_snipers.sh"]
