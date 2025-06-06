import os
import sys

import pytest


ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT_DIR)

from extract_best_realistic_odds import load_snapshots, find_best_odds


@pytest.mark.parametrize(
    "runner,expected",
    [
        ("fast runner", 4.5),
        ("unknown", None),
    ],
)
def test_find_best_odds(runner, expected):
    snapshots = load_snapshots("2025-06-07")
    # Race at 12:30 -> 750 minutes
    price = find_best_odds(12 * 60 + 30, "testville", runner, snapshots)
    assert price == expected
