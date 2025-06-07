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


if __name__ == "__main__":
    main()
