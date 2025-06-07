import json
import os
from pathlib import Path

import pandas as pd

from roi.roi_tracker_advised import main as roi_main
from roi.tag_roi_tracker import load_tips


def _create_sample_data(tmp_path: Path, date: str):
    pred_dir = tmp_path / "predictions" / date
    pred_dir.mkdir(parents=True)
    tips = [
        {
            "race": "12:00 Test",
            "name": "Good",
            "confidence": 0.9,
            "bf_sp": 5.0,
            "realistic_odds": 5.0,
            "tags": ["🧠 Monster NAP"],
        },
        {
            "race": "12:30 Test",
            "name": "Bad",
            "confidence": 0.9,
            "bf_sp": 10.0,
            "realistic_odds": 10.0,
            "tags": ["Other"],
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
            "horse": ["Good", "Bad"],
            "num": [8, 8],
            "pos": [1, 2],
            "race_name": ["", ""],
            "type": ["", ""],
            "class": ["", ""],
            "rating_band": ["", ""],
        }
    )
    df.to_csv(results_dir / f"{date.replace('-', '_')}.csv", index=False)


def test_load_tips_tag_filter(tmp_path):
    date = "2025-06-01"
    _create_sample_data(tmp_path, date)
    os.chdir(tmp_path)

    all_tips = load_tips(date, 0.0, use_sent=False)
    nap_tips = load_tips(date, 0.0, use_sent=False, tag="NAP")

    assert len(all_tips) == 2
    assert len(nap_tips) == 1
    assert nap_tips[0]["Horse"] == "good"


def test_roi_tracker_main_tag_filter(tmp_path, capsys):
    date = "2025-06-01"
    _create_sample_data(tmp_path, date)
    os.chdir(tmp_path)

    roi_main(date, "advised", 0.0, False, False, tag="NAP", show=True)
    out1 = capsys.readouterr().out
    assert "Tips: 1" in out1

    roi_main(date, "advised", 0.0, False, False, show=True)
    out2 = capsys.readouterr().out
    assert "Tips: 2" in out2
