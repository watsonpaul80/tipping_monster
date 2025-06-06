import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT_DIR)

from extract_best_realistic_odds import load_snapshots, find_best_odds


def test_find_best_odds_selects_latest_snapshot_before_race():
    snapshots = load_snapshots("2025-06-07")
    # Race at 12:30 -> 750 minutes
    price = find_best_odds(12 * 60 + 30, "testville", "fast runner", snapshots)
    assert price == 4.5


def test_find_best_odds_returns_none_for_unknown_runner():
    snapshots = load_snapshots("2025-06-07")
    price = find_best_odds(12 * 60 + 30, "testville", "unknown", snapshots)
    assert price is None
