#!/usr/bin/env python3
import argparse
import glob
import os
import subprocess
from datetime import datetime


def gather_roi_logs(log_base: str) -> list[str]:
    patterns = [
        os.path.join(log_base, "tips_results_*_advised.csv"),
        os.path.join(log_base, "roi", "tips_results_*_advised.csv"),
    ]
    logs: list[str] = []
    for pat in patterns:
        logs.extend(glob.glob(pat))
    return sorted(logs)


def should_retrain() -> bool:
    return datetime.today().weekday() == 0  # Monday


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="Self-training loop")
    parser.add_argument(
        "--retrain",
        action="store_true",
        help="Trigger retraining using recent ROI logs",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Ignore weekday check (always run)",
    )
    args = parser.parse_args(argv)

    if not args.retrain:
        print("Self-training not enabled. Use --retrain to start.")
        return

    if not args.force and not should_retrain():
        print("Skipping self-training (not scheduled day).")
        return

    log_base = os.getenv("TM_LOG_DIR", "logs")
    tip_logs = gather_roi_logs(log_base)

    if not tip_logs:
        print("No ROI logs found for self-training")
        return

    cmd = ["python", "train_model_v6.py", "--self-train"]
    print(f"Running: {' '.join(cmd)} with {len(tip_logs)} ROI logs")
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
