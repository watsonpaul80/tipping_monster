import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import stats_api


def _make_prediction_dir(tmp_path: Path) -> None:
    pred_dir = tmp_path / "predictions" / "2025-06-24"
    pred_dir.mkdir(parents=True)
    (pred_dir / "output.jsonl").write_text(json.dumps({"foo": "bar"}) + "\n")
    stats_api.PRED_DIR = tmp_path / "predictions"


def _make_roi_files(tmp_path: Path) -> None:
    roi_dir = tmp_path / "logs" / "roi"
    roi_dir.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame([{"a": 1}])
    df.to_csv(roi_dir / "roi_summary.csv", index=False)
    df.to_csv(roi_dir / "tag_roi_summary_sent.csv", index=False)
    stats_api.LOGS_DIR = tmp_path / "logs"


def test_endpoints(tmp_path):
    _make_prediction_dir(tmp_path)
    _make_roi_files(tmp_path)
    tips = stats_api.get_tips()
    assert tips[0]["foo"] == "bar"

    roi = stats_api.get_roi()
    assert roi[0]["a"] == 1

    tags = stats_api.get_tags()
    assert tags[0]["a"] == 1
