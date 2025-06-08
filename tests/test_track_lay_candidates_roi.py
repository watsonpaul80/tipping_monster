import pandas as pd

from track_lay_candidates_roi import lay_profit, summarise


def test_lay_profit():
    assert lay_profit("1", 3.0) == -2.0
    assert lay_profit("2", 5.0) == 1.0


def test_summarise():
    df = pd.DataFrame(
        {
            "Position": ["2", "1", "3"],
            "bf_sp": [3.0, 4.0, 2.5],
        }
    )
    summary = summarise(df)
    assert summary["bets"] == 3
    assert summary["wins"] == 1
    assert round(summary["profit"], 2) == 1 - 3 + 1  # 1 -3  +1 = -1
