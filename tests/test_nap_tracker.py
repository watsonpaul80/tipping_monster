import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
import os

import pandas as pd

from roi.nap_tracker import load_history, log_day, summarise_history


def test_log_day(tmp_path: Path):
    roi_dir = tmp_path / "logs" / "roi"
    roi_dir.mkdir(parents=True)

    csv_file = roi_dir / "tips_results_2025-06-01_advised.csv"
    df = pd.DataFrame(
        {
            "Position": [1, 2],
            "Profit": [4.0, -1.0],
            "Stake": [1.0, 1.0],
            "tags": ["['🧠 Monster NAP']", "['Other']"],
        }
    )
    df.to_csv(csv_file, index=False)

    os.environ["TM_DEV_MODE"] = "1"
    try:
        history_file = roi_dir / "nap_history.csv"
        row = log_day("2025-06-01", history_file, csv_file)
        assert row["Wins"] == 1
        assert row["Tips"] == 1

        history = load_history(history_file)
        assert len(history) == 1

        summary = summarise_history(history_file)
        assert summary["Wins"] == 1
        assert summary["Tips"] == 1
    finally:
        os.environ.pop("TM_DEV_MODE", None)
