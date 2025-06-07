import argparse
from pathlib import Path

from healthcheck_logs import check_logs
from ensure_sent_tips import ensure_sent_tips


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

    args = parser.parse_args(argv)

    if args.command == "healthcheck":
        check_logs(Path(args.out_log), args.date)
    elif args.command == "ensure-sent-tips":
        ensure_sent_tips(
            args.date,
            Path(args.predictions_dir),
            Path(args.dispatch_dir),
        )


if __name__ == "__main__":
    main()
