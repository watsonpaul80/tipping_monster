<<<<<<< HEAD
import argparse
from pathlib import Path

from healthcheck_logs import check_logs
from ensure_sent_tips import ensure_sent_tips
from tippingmonster.helpers import dispatch, send_daily_roi, generate_chart


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="Tipping Monster command line interface")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # healthcheck subcommand
    parser_health = subparsers.add_parser("healthcheck", help="Check expected log files exist")
    parser_health.add_argument("--date", help="Date YYYY-MM-DD (defaults to today)")
    parser_health.add_argument("--out-log", default="logs/healthcheck.log", help="Where to write status")

    # ensure-sent-tips subcommand
    parser_sent = subparsers.add_parser("ensure-sent-tips", help="Create sent tips file from predictions if missing")
    parser_sent.add_argument("date", help="Date YYYY-MM-DD")
    parser_sent.add_argument("--predictions-dir", default="predictions")
    parser_sent.add_argument("--dispatch-dir", default="logs/dispatch")

    # dispatch-tips subcommand
    parser_dispatch = subparsers.add_parser(
        "dispatch-tips", help="Run dispatch_tips.py"
    )
    parser_dispatch.add_argument("date", help="Date YYYY-MM-DD")
    parser_dispatch.add_argument("--telegram", action="store_true")
    parser_dispatch.add_argument("--dev", action="store_true")

    # send-roi subcommand
    parser_roi = subparsers.add_parser(
        "send-roi", help="Send daily ROI summary"
    )
    parser_roi.add_argument("--date")
    parser_roi.add_argument("--dev", action="store_true")

    # model-feature-importance subcommand
    parser_feat = subparsers.add_parser(
        "model-feature-importance", help="Generate SHAP feature importance chart"
    )
    parser_feat.add_argument("model")
    parser_feat.add_argument("--data")
    parser_feat.add_argument("--out", type=Path, default=Path("shap.png"))
    parser_feat.add_argument("--telegram", action="store_true")

    args = parser.parse_args(argv)

    if args.command == "healthcheck":
        check_logs(Path(args.out_log), args.date)
    elif args.command == "ensure-sent-tips":
        ensure_sent_tips(
            args.date,
            Path(args.predictions_dir),
            Path(args.dispatch_dir),
        )
    elif args.command == "dispatch-tips":
        dispatch(args.date, args.telegram, args.dev)
    elif args.command == "send-roi":
        send_daily_roi(args.date, args.dev)
    elif args.command == "model-feature-importance":
        generate_chart(args.model, args.data, args.out, args.telegram)
=======
"""Unified command line interface for Tipping Monster."""

from __future__ import annotations

import argparse
import os
import subprocess
from datetime import datetime
from pathlib import Path

from ensure_sent_tips import ensure_sent_tips
from healthcheck_logs import check_logs

from utils.validate_tips import main as validate_tips_main

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

    # validate-tips subcommand
    parser_validate = subparsers.add_parser(
        "validate-tips", help="Validate tips JSON for a given date"
    )
    parser_validate.add_argument("--date", type=valid_date, help="Date YYYY-MM-DD")
    parser_validate.add_argument("--predictions-dir", default="predictions")

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
        elif args.command == "validate-tips":
            argv = ["--date", args.date, "--predictions-dir", args.predictions_dir]
            validate_tips_main(argv)
    except Exception as exc:
        raise SystemExit(f"Error: {exc}") from exc
>>>>>>> origin/main


if __name__ == "__main__":
    main()
