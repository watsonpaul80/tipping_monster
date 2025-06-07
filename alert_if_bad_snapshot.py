import argparse
import json
from datetime import datetime
from pathlib import Path


def alert_if_bad_snapshot(date: str,
                          snapshot_dir: Path = Path('odds_snapshots'),
                          min_entries: int = 100,
                          alert_log: Path = Path('logs/alerts/bad_snapshot.log')) -> bool:
    """Return True and log if no snapshot or too few runners."""
    files = sorted(snapshot_dir.glob(f"{date}_*.json"))
    if not files:
        alert_log.parent.mkdir(parents=True, exist_ok=True)
        with alert_log.open('a') as fh:
            fh.write(f"{date} MISSING\n")
        print(f"⚠️ No snapshots found for {date}")
        return True
    latest = files[-1]
    try:
        data = json.loads(latest.read_text())
    except Exception:
        data = []
    if len(data) < min_entries:
        alert_log.parent.mkdir(parents=True, exist_ok=True)
        with alert_log.open('a') as fh:
            fh.write(f"{date} TOO_FEW {len(data)}\n")
        print(f"⚠️ Snapshot {latest.name} has only {len(data)} entries")
        return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description='Alert if odds snapshots missing or small')
    parser.add_argument('--date', default=datetime.now().strftime('%Y-%m-%d'))
    parser.add_argument('--min-entries', type=int, default=100)
    parser.add_argument('--snapshot-dir', default='odds_snapshots')
    parser.add_argument('--alert-log', default='logs/alerts/bad_snapshot.log')
    args = parser.parse_args()
    alert_if_bad_snapshot(args.date,
                          snapshot_dir=Path(args.snapshot_dir),
                          min_entries=args.min_entries,
                          alert_log=Path(args.alert_log))


if __name__ == '__main__':
    main()
