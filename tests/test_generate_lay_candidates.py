import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from generate_lay_candidates import find_danger_favs


def test_find_danger_favs_basic():
    df = pd.DataFrame(
        [
            {"race": "13:00 Ascot", "name": "A", "confidence": 0.9},
            {"race": "13:00 Ascot", "name": "B", "confidence": 0.4},
            {"race": "14:00 Ascot", "name": "C", "confidence": 0.3},
            {"race": "14:00 Ascot", "name": "D", "confidence": 0.8},
        ]
    )

    odds = [
        {"race": "Ascot 13:00", "horse": "B", "bf_sp": 2.0},
        {"race": "Ascot 13:00", "horse": "A", "bf_sp": 3.0},
        {"race": "Ascot 14:00", "horse": "C", "bf_sp": 3.0},
        {"race": "Ascot 14:00", "horse": "D", "bf_sp": 2.0},
    ]

    cands = find_danger_favs(df, odds, threshold=0.6)
    assert len(cands) == 1
    assert cands[0]["name"] == "B"
