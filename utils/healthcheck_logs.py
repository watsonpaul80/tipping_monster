#!/usr/bin/env python3
import argparse
from datetime import datetime
from pathlib import Path

EXPECTED_TEMPLATES = [
    "logs/dispatch/sent_tips_{date}.jsonl",
    "logs/inference/pipeline_{date}.log",
    "logs/inference/odds_0800_{date}.log",
    "logs/inference/odds_hourly_{date}.log",
]


def check_logs(out_log: Path, date: str | None = None) -> list[Path]:
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    missing: list[Path] = []
    for template in EXPECTED_TEMPLATES:
        p = Path(template.format(date=date))
        if not p.exists() or p.stat().st_size == 0:
            missing.append(p)
    out_log.parent.mkdir(parents=True, exist_ok=True)
    with out_log.open("a") as fh:
        if missing:
            for p in missing:
                fh.write(f"{date} MISSING {p}\n")
        else:
            fh.write(f"{date} OK\n")
    return missing


def main() -> None:
    parser = argparse.ArgumentParser(description="Check that expected logs exist and append result to healthcheck.log")
    parser.add_argument("--out-log", default="logs/healthcheck.log", help="Where to write health status")
    parser.add_argument("--date", help="Date string YYYY-MM-DD to check. Defaults to today")
    args = parser.parse_args()
    check_logs(Path(args.out_log), args.date)


if __name__ == "__main__":
    main()
