import json
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


def test_tmcli_dispatch_tips(tmp_path, monkeypatch):
    date = "2025-06-06"
    root = Path(__file__).resolve().parents[1]
    pred_dir = root / "predictions" / date
    pred_dir.mkdir(parents=True, exist_ok=True)
    tip = {"name": "Runner", "race": "12:00 Test", "confidence": 0.9, "bf_sp": 5.0}
    (pred_dir / "tips_with_odds.jsonl").write_text(json.dumps(tip) + "\n")
    (root / "logs" / "dev" / "dispatch").mkdir(parents=True, exist_ok=True)

    os.chdir(root)
    tmcli.main(["dispatch-tips", "--date", date, "--dev"])
    summary = pred_dir / "tips_summary.txt"
    sent = root / "logs" / "dev" / "dispatch" / f"sent_tips_{date}.jsonl"
    assert summary.exists()
    assert sent.exists()
    os.environ.pop("TM_DEV_MODE", None)


def test_tmcli_send_roi(tmp_path, monkeypatch):
    date = "2025-06-06"
    root = Path(__file__).resolve().parents[1]
    roi_dir = root / "logs" / "roi"
    roi_dir.mkdir(parents=True, exist_ok=True)
    csv = roi_dir / f"tips_results_{date}_advised.csv"
    csv.write_text("Position,Profit,Stake\n1,2.0,1.0\n2,0.5,1.0\n")
    (root / "logs" / "dev").mkdir(parents=True, exist_ok=True)

    os.chdir(root)
    tmcli.main(["send-roi", "--date", date, "--dev"])
    tg_log = root / "logs" / "dev" / "telegram.log"
    assert tg_log.exists()
    os.environ.pop("TM_DEV_MODE", None)
