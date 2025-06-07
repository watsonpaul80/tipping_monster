import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import tmcli


def test_tmcli_healthcheck(tmp_path):
    date = "2025-06-06"
    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / f"sent_tips_{date}.jsonl").write_text("ok")
    (logs / f"pipeline_{date}.log").write_text("ok")
    (logs / f"odds_0800_{date}.log").write_text("ok")
    (logs / f"odds_hourly_{date}.log").write_text("ok")

    os.chdir(tmp_path)
    tmcli.main(["healthcheck", "--date", date, "--out-log", "hc.log"])
    text = (tmp_path / "hc.log").read_text().strip()
    assert text.endswith("OK")


def test_tmcli_ensure_sent_tips(tmp_path):
    date = "2025-06-06"
    pred_dir = tmp_path / "predictions" / date
    pred_dir.mkdir(parents=True)
    (pred_dir / "tips_with_odds.jsonl").write_text("tip")

    os.chdir(tmp_path)
    tmcli.main(
        [
            "ensure-sent-tips",
            date,
            "--predictions-dir",
            "predictions",
            "--dispatch-dir",
            "logs/dispatch",
        ]
    )
    sent = tmp_path / "logs/dispatch" / f"sent_tips_{date}.jsonl"
    assert sent.exists()
    assert sent.read_text() == "tip"


def test_tmcli_healthcheck_missing_files(tmp_path):
    """healthcheck should log missing files when expected logs are absent."""
    date = "2025-06-06"
    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / f"sent_tips_{date}.jsonl").write_text("ok")

    os.chdir(tmp_path)
    tmcli.main(["healthcheck", "--date", date, "--out-log", "hc.log"])
    text = (tmp_path / "hc.log").read_text()
    assert text.count("MISSING") == 3


def test_tmcli_ensure_sent_tips_missing_pred(tmp_path):
    """ensure-sent-tips should do nothing when predictions are absent."""
    date = "2025-06-06"
    pred_dir = tmp_path / "predictions" / date
    pred_dir.mkdir(parents=True)

    os.chdir(tmp_path)
    tmcli.main(
        [
            "ensure-sent-tips",
            date,
            "--predictions-dir",
            "predictions",
            "--dispatch-dir",
            "logs/dispatch",
        ]
    )
    sent = tmp_path / "logs/dispatch" / f"sent_tips_{date}.jsonl"
    assert not sent.exists()
