import os
import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.alert_if_bad_snapshot import alert_if_bad_snapshot


def test_alert_when_missing(tmp_path):
    os.chdir(tmp_path)
    triggered = alert_if_bad_snapshot("2025-06-07", snapshot_dir=Path('snaps'), alert_log=Path('alert.log'))
    assert triggered
    assert (tmp_path / 'alert.log').exists()


def test_alert_when_too_small(tmp_path):
    snap_dir = tmp_path / 'snaps'
    snap_dir.mkdir()
    (snap_dir / '2025-06-07_1200.json').write_text('[]')
    os.chdir(tmp_path)
    triggered = alert_if_bad_snapshot("2025-06-07", snapshot_dir=snap_dir, min_entries=5, alert_log=Path('alert.log'))
    assert triggered
    assert (tmp_path / 'alert.log').exists()


def test_no_alert_when_ok(tmp_path):
    snap_dir = tmp_path / 'snaps'
    snap_dir.mkdir()
    data = [{"a": 1}] * 10
    with open(snap_dir / '2025-06-07_1200.json', 'w') as f:
        json.dump(data, f)
    os.chdir(tmp_path)
    triggered = alert_if_bad_snapshot("2025-06-07", snapshot_dir=snap_dir, min_entries=5, alert_log=Path('alert.log'))
    assert not triggered
    assert not (tmp_path / 'alert.log').exists()
