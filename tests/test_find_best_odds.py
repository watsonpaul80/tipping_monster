import os
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.extract_best_realistic_odds import find_best_odds, load_snapshots


def write_snapshot(dir_path, date, time_label, runners):
    file = dir_path / f"{date}_{time_label}.json"
    with open(file, "w") as f:
        json.dump(runners, f)


def test_find_best_odds_from_earlier_snapshots(tmp_path):
    snap_dir = tmp_path / "odds_snapshots"
    snap_dir.mkdir()
    date = "2025-06-07"

    write_snapshot(snap_dir, date, "0930", [{"race": "10:00 Chelmsford", "horse": "My Horse", "price": 5.0}])
    write_snapshot(snap_dir, date, "0945", [{"race": "10:00 Chelmsford", "horse": "My Horse", "price": 4.5}])
    write_snapshot(snap_dir, date, "1005", [{"race": "10:00 Chelmsford", "horse": "My Horse", "price": 4.0}])

    os.chdir(tmp_path)
    snapshots = load_snapshots(date)
    odds = find_best_odds(10 * 60, "chelmsford", "my horse", snapshots)
    assert odds == 4.5


def test_find_best_odds_returns_none_when_missing(tmp_path):
    snap_dir = tmp_path / "odds_snapshots"
    snap_dir.mkdir()
    date = "2025-06-07"

    write_snapshot(snap_dir, date, "0930", [{"race": "10:00 Chelmsford", "horse": "Other Horse", "price": 5.0}])
    os.chdir(tmp_path)
    snapshots = load_snapshots(date)
    odds = find_best_odds(10 * 60, "chelmsford", "my horse", snapshots)
    assert odds is None
