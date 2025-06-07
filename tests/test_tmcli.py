import json
import os
import sys
from datetime import date
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
    logs = tmp_path / "logs" / "dispatch"
    logs.mkdir(parents=True)
    (logs / f"sent_tips_{date_str}.jsonl").write_text("ok")

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


def test_tmcli_ensure_sent_tips_missing_pred(tmp_path):
    date_str = "2025-06-06"
    pred_dir = tmp_path / "predictions" / date_str
    pred_dir.mkdir(parents=True)

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


def test_tmcli_dispatch_tips(tmp_path):
    date_str = "2025-06-06"
    root = Path(__file__).resolve().parents[1]
    pred_dir = root / "predictions" / date_str
    pred_dir.mkdir(parents=True, exist_ok=True)
    tip = {"name": "Runner", "race": "12:00 Test", "confidence": 0.9, "bf_sp": 5.0}
    (pred_dir / "tips_with_odds.jsonl").write_text(json.dumps(tip) + "\n")
    (root / "logs" / "dev" / "dispatch").mkdir(parents=True, exist_ok=True)

    os.chdir(root)
    tmcli.main(["dispatch-tips", "--date", date_str, "--dev"])
    summary = pred_dir / "tips_summary.txt"
    sent = root / "logs" / "dev" / "dispatch" / f"sent_tips_{date_str}.jsonl"
    assert summary.exists()
    assert sent.exists()
    os.environ.pop("TM_DEV_MODE", None)


def test_tmcli_send_roi(tmp_path):
    date_str = "2025-06-06"
    root = Path(__file__).resolve().parents[1]
    roi_dir = root / "logs" / "roi"
    roi_dir.mkdir(parents=True, exist_ok=True)
    csv = roi_dir / f"tips_results_{date_str}_advised.csv"
    csv.write_text("Position,Profit,Stake\n1,2.0,1.0\n2,0.5,1.0\n")
    (root / "logs" / "dev").mkdir(parents=True, exist_ok=True)

    os.chdir(root)
    tmcli.main(["send-roi", "--date", date_str, "--dev"])
    tg_log = root / "logs" / "dev" / "telegram.log"
    assert tg_log.exists()
    os.environ.pop("TM_DEV_MODE", None)


def test_tmcli_model_feature_importance(tmp_path):
    import pandas as pd
    import xgboost as xgb

    X = pd.DataFrame({"a": [0, 1, 2, 3], "b": [1, 2, 3, 4]})
    y = [0, 1, 0, 1]
    model = xgb.XGBClassifier(use_label_encoder=False, eval_metric="logloss")
    model.fit(X, y)

    model_path = tmp_path / "model.bst"
    model.save_model(model_path)
    features_path = tmp_path / "features.json"
    json.dump(list(X.columns), open(features_path, "w"))
    data_path = tmp_path / "data.jsonl"
    X.to_json(data_path, orient="records", lines=True)

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
