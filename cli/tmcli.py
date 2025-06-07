import argparse
from datetime import date
from pathlib import Path

from utils.healthcheck_logs import check_logs
from utils.ensure_sent_tips import ensure_sent_tips


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        description="Tipping Monster command line interface"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

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
    parser_dispatch.add_argument("--date", help="Date YYYY-MM-DD", default=None)
    parser_dispatch.add_argument("--telegram", action="store_true")
    parser_dispatch.add_argument("--dev", action="store_true")

    # send-roi subcommand
    parser_roi = subparsers.add_parser(
        "send-roi", help="Send daily ROI summary to Telegram"
    )
    parser_roi.add_argument("--date", help="Date YYYY-MM-DD", default=None)
    parser_roi.add_argument("--dev", action="store_true")

    args = parser.parse_args(argv)

    if args.command == "healthcheck":
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
        dispatch(
            date=args.date or date.today().isoformat(),
            telegram=args.telegram,
            dev=args.dev,
        )
    elif args.command == "send-roi":
        send_daily_roi(date=args.date, dev=args.dev)


if __name__ == "__main__":
    main()
