import json
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

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


def _create_weighted_data(tmp_path: Path) -> None:
    """Create tips across two dates to test time-decay weighting."""
    recent_date = "2025-06-01"
    old_date = "2025-02-01"

    # Recent winning tip
    pred_dir = tmp_path / "predictions" / recent_date
    pred_dir.mkdir(parents=True)
    with open(pred_dir / "tips_with_odds.jsonl", "w") as f:
        f.write(
            json.dumps(
                {
                    "race": "12:00 Test",
                    "name": "RecentWinner",
                    "confidence": 0.9,
                    "bf_sp": 2.0,
                    "realistic_odds": 2.0,
                    "tags": ["WeightTag"],
                }
            )
            + "\n"
        )

    results_dir = tmp_path / "rpscrape" / "data" / "dates" / "all"
    results_dir.mkdir(parents=True)
    df = pd.DataFrame(
        {
            "off": ["12:00"],
            "course": ["Test"],
            "horse": ["RecentWinner"],
            "num": [8],
            "pos": [1],
            "race_name": [""],
            "type": [""],
            "class": [""],
            "rating_band": [""],
        }
    )
    df.to_csv(results_dir / f"{recent_date.replace('-', '_')}.csv", index=False)

    # Older losing tip
    pred_dir = tmp_path / "predictions" / old_date
    pred_dir.mkdir(parents=True)
    with open(pred_dir / "tips_with_odds.jsonl", "w") as f:
        f.write(
            json.dumps(
                {
                    "race": "12:30 Test",
                    "name": "OldLoser",
                    "confidence": 0.9,
                    "bf_sp": 3.0,
                    "realistic_odds": 3.0,
                    "tags": ["WeightTag"],
                }
            )
            + "\n"
        )

    df = pd.DataFrame(
        {
            "off": ["12:30"],
            "course": ["Test"],
            "horse": ["OldLoser"],
            "num": [8],
            "pos": [5],
            "race_name": [""],
            "type": [""],
            "class": [""],
            "rating_band": [""],
        }
    )
    df.to_csv(results_dir / f"{old_date.replace('-', '_')}.csv", index=False)


def test_compute_summary(tmp_path):
    date = "2025-06-01"
    _create_sample_data(tmp_path, date)
    os.chdir(tmp_path)
    summary = compute_summary("predictions", "rpscrape/data/dates/all", min_conf=0.0)

    assert "🧠 Monster NAP" in summary.index
    assert summary.loc["🧠 Monster NAP", "Wins"] == 1
    assert summary.loc["Danger Fav", "Tips"] == 1
    assert summary.loc["Danger Fav", "Wins"] == 0


def test_time_decay_weighting(tmp_path):
    _create_weighted_data(tmp_path)
    os.chdir(tmp_path)
    summary = compute_summary("predictions", "rpscrape/data/dates/all", min_conf=0.0)

    assert "WeightTag" in summary.index
    tips = summary.loc["WeightTag", "Tips"]
    wins = summary.loc["WeightTag", "Wins"]
    win_pct = summary.loc["WeightTag", "Win %"]

    assert round(tips, 2) == 1.1
    assert round(wins, 2) == 1.0
    assert abs(win_pct - 90.91) < 0.01
