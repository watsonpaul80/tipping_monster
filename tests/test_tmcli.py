import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

import pandas as pd
import xgboost as xgb

sys.path.append(str(Path(__file__).resolve().parents[1]))

from cli import tmcli


def build_dummy_model(path: Path) -> None:
    features = [
        "draw",
        "or",
        "rpr",
        "lbs",
        "age",
        "dist_f",
        "class",
        "going",
        "prize",
    ]
    X = pd.DataFrame([[0] * len(features), [1] * len(features)], columns=features)
    y = [0, 1]
    model = xgb.XGBClassifier(
        use_label_encoder=False, eval_metric="logloss", n_estimators=1
    )
    model.fit(X, y)
    model.get_booster().save_model(path)


def test_tmcli_healthcheck(tmp_path):
    date_str = "2025-06-06"
    logs = tmp_path / "logs"
    (logs / "dispatch").mkdir(parents=True, exist_ok=True)
    (logs / "inference").mkdir(parents=True, exist_ok=True)
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

    logs = tmp_path / "logs" / "dispatch"
    logs.mkdir(parents=True)
    (logs / f"sent_tips_{date_str}.jsonl").write_text("ok")
    logs = tmp_path / "logs"
    (logs / "dispatch").mkdir(parents=True, exist_ok=True)
    (logs / "inference").mkdir(parents=True, exist_ok=True)
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
    tmcli.main(
        [
            "ensure-sent-tips",
            date_str,
            "--predictions-dir",
            "predictions",
            "--dispatch-dir",
            "logs/dispatch",
        ]
    )
    sent = tmp_path / "logs/dispatch" / f"sent_tips_{date_str}.jsonl"
    assert sent.exists()
    assert sent.read_text() == "tip"


def test_tmcli_dispatch_tips(monkeypatch, tmp_path):
    date_str = "2025-06-06"

    calls = {}
    monkeypatch.delenv("TM_DEV_MODE", raising=False)
    monkeypatch.delenv("TM_LOG_DIR", raising=False)

    os.chdir(tmp_path)
    tmcli.main(
        [
            "ensure-sent-tips",
            date_str,
            "--predictions-dir",
            "predictions",
            "--dispatch-dir",
            "logs/dispatch",
        ]
    )
    sent = tmp_path / "logs/dispatch" / f"sent_tips_{date_str}.jsonl"
    assert not sent.exists()

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


def test_tmcli_send_roi(monkeypatch, tmp_path):
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

    model_path = tmp_path / "model.bst"
    build_dummy_model(model_path)
    data_path = tmp_path / "data.jsonl"
    with open(data_path, "w") as f:
        json.dump(
            {
                "draw": 0,
                "or": 0,
                "rpr": 0,
                "lbs": 0,
                "age": 0,
                "dist_f": 0,
                "class": 0,
                "going": "G",
                "prize": 0,
            },
            f,
        )
        f.write("\n")

    os.chdir(tmp_path)
    tmcli.main(
        [
            "model-feature-importance",
            "--model",
            str(model_path),
            "--data",
            str(data_path),
            "--out-dir",
            "logs/model",
        ]
    )
    out = tmp_path / "logs/model" / f"feature_importance_{date.today().isoformat()}.png"
    assert out.exists()
