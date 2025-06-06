import argparse
import os
import subprocess


def run_pipeline(date: str) -> None:
    env = os.environ.copy()
    env["TM_DATE"] = date
    subprocess.run(["bash", "run_pipeline_with_venv.sh"], check=True, env=env)


def run_roi_pipeline(date: str) -> None:
    env = os.environ.copy()
    env["DATE"] = date
    subprocess.run(["bash", "run_roi_pipeline.sh", date], check=True, env=env)


def run_sniper_schedule() -> None:
    subprocess.run(["bash", "generate_and_schedule_snipers.sh"], check=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Tipping Monster CLI")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("pipeline", help="Run full daily pipeline")
    p.add_argument("--date", required=True, help="Date in YYYY-MM-DD")
    p.set_defaults(func=lambda args: run_pipeline(args.date))

    r = sub.add_parser("roi", help="Run ROI pipeline")
    r.add_argument("--date", required=True, help="Date in YYYY-MM-DD")
    r.set_defaults(func=lambda args: run_roi_pipeline(args.date))

    s = sub.add_parser("sniper", help="Generate and schedule sniper jobs")
    s.set_defaults(func=lambda args: run_sniper_schedule())

    return parser


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
