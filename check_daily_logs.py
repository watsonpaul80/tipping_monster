import argparse
from datetime import datetime
from pathlib import Path


def status(path: Path) -> str:
    return "✅" if path.exists() and path.stat().st_size > 0 else "❌"


def main(date_str: str) -> None:
    logs = {
        "tips_results": Path(f"logs/tips_results_{date_str}_advised.csv"),
        "sent_tips": Path(f"logs/sent_tips_{date_str}.jsonl"),
        "realistic_odds": Path(f"logs/sent_tips_{date_str}_realistic.jsonl"),
    }
    for label, path in logs.items():
        print(f"{label}: {status(path)}")

    snapshots = list(Path("odds_snapshots").glob(f"{date_str}_*.json"))
    snap_ok = any(p.stat().st_size > 0 for p in snapshots)
    print(f"snapshots: {'✅' if snap_ok else '❌'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check expected logs for a date")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"), help="YYYY-MM-DD")
    args = parser.parse_args()
    main(args.date)
