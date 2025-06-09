import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from simulate_staking import simulate


def test_simulate_basic():
    df = pd.DataFrame(
        {
            "Odds": [3.0, 5.0, 2.5],
            "Confidence": [0.8, 0.9, 0.75],
            "Position": ["1", "2", "0"],
            "Runners": [8, 12, 8],
            "Race Name": ["Hcp", "Hcp", "Hcp"],
        }
    )

    results = simulate(df)
    level = results["level"]
    assert round(level["profit"], 2) != 0
    assert level["stake"] == 3.0
    confidence = results["confidence"]
    assert confidence["stake"] > level["stake"]
    value = results["value"]
    assert value["stake"] >= 0
