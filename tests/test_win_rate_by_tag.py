import json
import os
from pathlib import Path

import pandas as pd

from win_rate_by_tag import compute_summary


def _create_sample_data(tmp_path: Path, date: str) -> None:
    pred_dir = tmp_path / "predictions" / date
    pred_dir.mkdir(parents=True)
    tips = [
        {
            "race": "12:00 Test",
            "name": "NapHorse",
            "confidence": 0.9,
            "bf_sp": 5.0,
            "realistic_odds": 5.0,
            "tags": ["🧠 Monster NAP", "Each-Way"],
        },
        {
            "race": "12:30 Test",
            "name": "DangerHorse",
            "confidence": 0.9,
            "bf_sp": 4.0,
            "realistic_odds": 4.0,
            "tags": ["Danger Fav"],
        },
    ]
    with open(pred_dir / "tips_with_odds.jsonl", "w") as f:
        for tip in tips:
            f.write(json.dumps(tip) + "\n")

    results_dir = tmp_path / "rpscrape" / "data" / "dates" / "all"
    results_dir.mkdir(parents=True)
    df = pd.DataFrame(
        {
            "off": ["12:00", "12:30"],
            "course": ["Test", "Test"],
            "horse": ["NapHorse", "DangerHorse"],
            "num": [8, 8],
            "pos": [1, 3],
            "race_name": ["", ""],
            "type": ["", ""],
            "class": ["", ""],
            "rating_band": ["", ""],
        }
    )
    df.to_csv(results_dir / f"{date.replace('-', '_')}.csv", index=False)


def test_compute_summary(tmp_path):
    date = "2025-06-01"
    _create_sample_data(tmp_path, date)
    os.chdir(tmp_path)
    summary = compute_summary("predictions", "rpscrape/data/dates/all", min_conf=0.0)

    assert "🧠 Monster NAP" in summary.index
    assert summary.loc["🧠 Monster NAP", "Wins"] == 1
    assert summary.loc["Danger Fav", "Tips"] == 1
    assert summary.loc["Danger Fav", "Wins"] == 0
