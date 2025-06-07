import json
import os
from datetime import date
import sys
import subprocess
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from cli import tmcli


def test_tmcli_healthcheck(tmp_path):
    date_str = "2025-06-06"
    logs = tmp_path / "logs"
    (logs / "dispatch").mkdir(parents=True)
    (logs / "inference").mkdir(parents=True)
    (logs / "dispatch" / f"sent_tips_{date_str}.jsonl").write_text("ok")
    (logs / "inference" / f"pipeline_{date_str}.log").write_text("ok")
    (logs / "inference" / f"odds_0800_{date_str}.log").write_text("ok")
    (logs / "inference" / f"odds_hourly_{date_str}.log").write_text("ok")

    os.chdir(tmp_path)
    tmcli.main(["healthcheck", "--date", date_str, "--out-log", "hc.log"])
    text = (tmp_path / "hc.log").read_text().strip()
    assert text.endswith("OK")


def test_tmcli_healthcheck_missing_files(tmp_path):
    date_str = "2025-06-06"
    logs = tmp_path / "logs"
    (logs / "dispatch").mkdir(parents=True)
    (logs / "inference").mkdir(parents=True)
    (logs / "dispatch" / f"sent_tips_{date_str}.jsonl").write_text("ok")

    os.chdir(tmp_path)
    tmcli.main(["healthcheck", "--date", date_str, "--out-log", "hc.log"])
    text = (tmp_path / "hc.log").read_text()
    assert text.count("MISSING") == 3


def test_tmcli_ensure_sent_tips(tmp_path):
    date_str = "2025-06-06"
    pred_dir = tmp_path / "predictions" / date_str
    pred_dir.mkdir(parents=True)
    (pred_dir / "tips_with_odds.jsonl").write_text("tip")

    os.chdir(tmp_path)
    tmcli.main([
        "ensure-sent-tips",
        date_str,
        "--predictions-dir", "predictions",
        "--dispatch-dir", "logs/dispatch",
    ])
    sent = tmp_path / "logs/dispatch" / f"sent_tips_{date_str}.jsonl"
    assert sent.exists()
    assert sent.read_text() == "tip"


def test_tmcli_dispatch_tips(monkeypatch):
    calls = {}
    monkeypatch.delenv("TM_DEV_MODE", raising=False)
    monkeypatch.delenv("TM_LOG_DIR", raising=False)

    def fake_run(cmd, check):
        calls["cmd"] = cmd
        calls["check"] = check

    monkeypatch.setattr(subprocess, "run", fake_run)
    tmcli.main(["dispatch-tips", "2025-06-06", "--telegram", "--dev"])
    assert "dispatch_tips.py" in calls["cmd"][1]
    assert "--telegram" in calls["cmd"]
    assert "--dev" in calls["cmd"]
    assert os.environ["TM_DEV_MODE"] == "1"
    assert os.environ["TM_LOG_DIR"] == "logs/dev"
    monkeypatch.delenv("TM_DEV_MODE", raising=False)
    monkeypatch.delenv("TM_LOG_DIR", raising=False)


def test_tmcli_send_roi(monkeypatch):
    calls = {}
    monkeypatch.delenv("TM_DEV_MODE", raising=False)
    monkeypatch.delenv("TM_LOG_DIR", raising=False)

    def fake_run(cmd, check):
        calls["cmd"] = cmd
        calls["check"] = check

    monkeypatch.setattr(subprocess, "run", fake_run)
    tmcli.main(["send-roi", "--date", "2025-06-05", "--dev"])
    assert "send_daily_roi_summary.py" in calls["cmd"][1]
    assert "--date" in calls["cmd"]
    assert "2025-06-05" in calls["cmd"]
    assert os.environ["TM_DEV_MODE"] == "1"
    assert os.environ["TM_LOG_DIR"] == "logs/dev"
    monkeypatch.delenv("TM_DEV_MODE", raising=False)
    monkeypatch.delenv("TM_LOG_DIR", raising=False)


