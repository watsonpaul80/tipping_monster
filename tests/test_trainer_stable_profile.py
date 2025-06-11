import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd

from core.trainer_stable_profile import compute_trainer_stats


def test_compute_trainer_stats_basic(tmp_path):
    df = pd.DataFrame(
        {
            "Trainer": ["A", "A", "B", "B"],
            "Position": ["1", "2", "1", "3"],
            "BFSP": [3.0, 5.0, 4.0, 6.0],
        }
    )
    stats = compute_trainer_stats(df)
    a = stats[stats["Trainer"] == "A"].iloc[0]
    b = stats[stats["Trainer"] == "B"].iloc[0]
    assert a["Runs"] == 2 and a["Wins"] == 1
    assert b["Runs"] == 2 and b["Wins"] == 1
    assert a["Win %"] == 50.0
    assert round(float(a["ROI %"]), 2) == round(((3.0 - 1) - 1) / 2 * 100, 2)
    assert round(float(b["ROI %"]), 2) == round(((4.0 - 1) - 1) / 2 * 100, 2)
