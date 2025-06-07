import sys
from pathlib import Path

import pandas as pd
from pandas.testing import assert_frame_equal

sys.path.append(str(Path(__file__).resolve().parents[1]))

from roi_by_confidence_band import summarise


def test_summarise_basic():
    df = pd.DataFrame(
        {
            "Confidence": [0.82, 0.83, 0.87, 0.93],
            "Profit": [1, -1, 0.5, 1],
            "Stake": [1, 1, 1, 2],
            "Position": ["1", "2", "1", "0"],
        }
    )

    summary = summarise(df).reset_index(drop=True)

    expected = pd.DataFrame(
        {
            "Band": ["0.80–0.85", "0.85–0.90", "0.90+"],
            "Tips": [2.0, 1.0, 1.0],
            "Wins": [1.0, 1.0, 0.0],
            "Stake": [2.0, 1.0, 2.0],
            "Profit": [0.0, 0.5, 1.0],
            "Win %": [50.0, 100.0, 0.0],
            "ROI %": [0.0, 50.0, 50.0],
        }
    )

    assert_frame_equal(summary, expected)
