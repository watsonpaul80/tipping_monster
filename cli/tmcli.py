import argparse
import os
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

from model_feature_importance import generate_chart
from utils.ensure_sent_tips import ensure_sent_tips
from utils.healthcheck_logs import check_logs
from utils.validate_tips import main as validate_tips_main
from tippingmonster import repo_path

ROOT = Path(__file__).resolve().parents[1]


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
    subprocess.run(cmd, check=True, env=env)


def dispatch(date: str, telegram: bool = False, dev: bool = False) -> None:
    cmd = [sys.executable, str(repo_path("core", "dispatch_tips.py")), "--date", date]
    if telegram:
        cmd.append("--telegram")
    if dev:
        cmd.append("--dev")
        os.environ["TM_DEV_MODE"] = "1"
        os.environ["TM_LOG_DIR"] = "logs/dev"
    subprocess.run(cmd, check=True)


def send_roi(date: str | None = None, dev: bool = False) -> None:
    cmd = [sys.executable, str(repo_path("roi", "send_daily_roi_summary.py"))]
    if date:
        cmd += ["--date", date]
    if dev:
        cmd.append("--dev")
        os.environ["TM_DEV_MODE"] = "1"
        os.environ["TM_LOG_DIR"] = "logs/dev"
    subprocess.run(cmd, check=True)


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
    parser_roi_pipe = subparsers.add_parser(
        "roi", help="Run ROI pipeline for a given date"
    )
    parser_roi_pipe.add_argument("--date", type=valid_date, help="Date YYYY-MM-DD")
    parser_roi_pipe.add_argument(
        "--dev", action="store_true", help="Enable development mode"
    )

    # sniper subcommand (placeholder)
    parser_sniper = subparsers.add_parser(
        "sniper", help="Run sniper jobs (if available)"
    )
    parser_sniper.add_argument(
        "--dev", action="store_true", help="Enable development mode for sniper jobs"
    )

    # healthcheck subcommand
    parser_health = subparsers.add_parser(
        "healthcheck", help="Check expected log files exist"
    )
    parser_health.add_argument("--date", help="Date YYYY-MM-DD (defaults to today)")
    parser_health.add_argument(
        "--out-log", default="logs/healthcheck.log", help="Where to write status"
    )

    # ensure-sent-tips subcommand
    parser_sent = subparsers.add_parser(
        "ensure-sent-tips", help="Create sent tips file from predictions if missing"
    )
    parser_sent.add_argument("date", help="Date YYYY-MM-DD")
    parser_sent.add_argument("--predictions-dir", default="predictions")
    parser_sent.add_argument("--dispatch-dir", default="logs/dispatch")

    # validate-tips subcommand
    parser_validate = subparsers.add_parser(
        "validate-tips", help="Validate tips JSON for a given date"
    )
    parser_validate.add_argument("--date", help="Date YYYY-MM-DD", default=None)
    parser_validate.add_argument("--predictions-dir", default="predictions")

    # model-feature-importance subcommand
    parser_feat = subparsers.add_parser(
        "model-feature-importance",
        help="Generate SHAP feature importance chart",
    )
    parser_feat.add_argument("--model", default="tipping-monster-xgb-model.bst")
    parser_feat.add_argument("--data", help="Input JSONL with features")
    parser_feat.add_argument("--out-dir", default="logs/model")
    parser_feat.add_argument("--telegram", action="store_true")

    # dispatch-tips subcommand
    parser_dispatch = subparsers.add_parser(
        "dispatch-tips", help="Format and optionally send today's tips"
    )
    parser_dispatch.add_argument("date", nargs="?", help="Date YYYY-MM-DD")
    parser_dispatch.add_argument("--date", help="Date YYYY-MM-DD", dest="date_opt", default=None)
    parser_dispatch.add_argument("--telegram", action="store_true")
    parser_dispatch.add_argument("--dev", action="store_true")

    # send-roi subcommand
    parser_roi = subparsers.add_parser(
        "send-roi", help="Send daily ROI summary to Telegram"
    )
    parser_roi.add_argument("--date", help="Date YYYY-MM-DD", default=None)
    parser_roi.add_argument("--dev", action="store_true")

    args = parser.parse_args(argv)

    if args.command == "pipeline":
        cmd = [str(ROOT / "core" / "run_pipeline_with_venv.sh")]
        if args.dev:
            cmd.append("--dev")
        run_command(["bash", *cmd], args.dev)

    elif args.command == "roi":
        cmd = [str(ROOT / "roi" / "run_roi_pipeline.sh")]
        if args.date:
            cmd.append(args.date)
        run_command(["bash", *cmd], args.dev)

    elif args.command == "sniper":
        raise RuntimeError("Sniper functionality is not included in this distribution")

    elif args.command == "healthcheck":
        check_logs(Path(args.out_log), args.date)

    elif args.command == "ensure-sent-tips":
        ensure_sent_tips(
            args.date,
            Path(args.predictions_dir),
            Path(args.dispatch_dir),
        )

    elif args.command == "model-feature-importance":
        out = generate_chart(
            args.model,
            args.data,
            Path(args.out_dir) / f"feature_importance_{date.today().isoformat()}.png",
            telegram=args.telegram,
        )
        print(out)

    elif args.command == "dispatch-tips":
        date_arg = args.date or args.date_opt
        dispatch(
            date=date_arg or date.today().isoformat(),
            telegram=args.telegram,
            dev=args.dev,
        )

    elif args.command == "validate-tips":
        argv = ["--date", args.date] if args.date else []
        argv += ["--predictions-dir", args.predictions_dir]
        validate_tips_main(argv)

    elif args.command == "send-roi":
        send_roi(date=args.date, dev=args.dev)


if __name__ == "__main__":
    main()
