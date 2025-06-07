"""Unified command line interface for Tipping Monster."""

from __future__ import annotations

import argparse
import os
import subprocess
from datetime import datetime
from pathlib import Path

from ensure_sent_tips import ensure_sent_tips
from healthcheck_logs import check_logs

ROOT = Path(__file__).resolve().parent


def valid_date(value: str) -> str:
    """Return ``value`` if it matches ``YYYY-MM-DD`` else raise ``ArgumentTypeError``."""
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid date: {value}. Use YYYY-MM-DD"
        ) from exc
    return value


def run_command(cmd: list[str], dev: bool) -> None:
    """Run ``cmd`` with optional ``TM_DEV_MODE`` set."""
    env = os.environ.copy()
    if dev:
        env["TM_DEV_MODE"] = "1"
    try:
        subprocess.run(cmd, check=True, env=env)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Script not found: {cmd[0]}") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Command failed with exit code {exc.returncode}") from exc


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        description="Tipping Monster command line interface"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # pipeline subcommand
    parser_pipe = subparsers.add_parser("pipeline", help="Run the full daily pipeline")
    parser_pipe.add_argument(
        "--dev",
        action="store_true",
        help="Enable development mode (no Telegram/S3 uploads)",
    )

    # roi subcommand
    parser_roi = subparsers.add_parser("roi", help="Run ROI pipeline for a given date")
    parser_roi.add_argument("--date", type=valid_date, help="Date YYYY-MM-DD")
    parser_roi.add_argument(
        "--dev",
        action="store_true",
        help="Enable development mode (affects downstream scripts)",
    )

    # sniper subcommand (placeholder)
    parser_sniper = subparsers.add_parser(
        "sniper", help="Run sniper jobs (if available)"
    )
    parser_sniper.add_argument(
        "--dev",
        action="store_true",
        help="Enable development mode for sniper jobs",
    )

    # healthcheck subcommand
    parser_health = subparsers.add_parser(
        "healthcheck", help="Check expected log files exist"
    )
    parser_health.add_argument("--date", type=valid_date, help="Date YYYY-MM-DD")
    parser_health.add_argument(
        "--out-log",
        default="logs/healthcheck.log",
        help="Where to write status",
    )
    parser_health.add_argument(
        "--dev",
        action="store_true",
        help="Enable development mode (unused)",
    )

    # ensure-sent-tips subcommand (legacy)
    parser_sent = subparsers.add_parser(
        "ensure-sent-tips",
        help="Create sent tips file from predictions if missing",
    )
    parser_sent.add_argument("date", type=valid_date, help="Date YYYY-MM-DD")
    parser_sent.add_argument("--predictions-dir", default="predictions")
    parser_sent.add_argument("--dispatch-dir", default="logs/dispatch")

    args = parser.parse_args(argv)

    try:
        if args.command == "pipeline":
            cmd = [str(ROOT / "run_pipeline_with_venv.sh")]
            if args.dev:
                cmd.append("--dev")
            run_command(["bash", *cmd], args.dev)
        elif args.command == "roi":
            cmd = [str(ROOT / "run_roi_pipeline.sh")]
            if args.date:
                cmd.append(args.date)
            run_command(["bash", *cmd], args.dev)
        elif args.command == "sniper":
            raise RuntimeError(
                "Sniper functionality is not included in this distribution"
            )
        elif args.command == "healthcheck":
            check_logs(Path(args.out_log), args.date)
        elif args.command == "ensure-sent-tips":
            ensure_sent_tips(
                args.date,
                Path(args.predictions_dir),
                Path(args.dispatch_dir),
            )
    except Exception as exc:
        raise SystemExit(f"Error: {exc}") from exc


if __name__ == "__main__":
    main()
