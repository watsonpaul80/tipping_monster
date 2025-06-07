import argparse
import os
import subprocess


def run_pipeline(date: str, dev: bool = False) -> None:
    env = os.environ.copy()
    env["TM_DATE"] = date
    if dev:
        env["TM_DEV"] = "1"
    subprocess.run(["bash", "run_pipeline_with_venv.sh"], check=True, env=env)


def run_roi_pipeline(date: str, dev: bool = False) -> None:
    env = os.environ.copy()
    env["DATE"] = date
    if dev:
        env["TM_DEV"] = "1"
    subprocess.run(["bash", "run_roi_pipeline.sh", date], check=True, env=env)


def run_sniper_schedule(dev: bool = False) -> None:
    env = os.environ.copy()
    if dev:
        env["TM_DEV"] = "1"
    subprocess.run(["bash", "generate_and_schedule_snipers.sh"], check=True, env=env)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Tipping Monster CLI")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("pipeline", help="Run full daily pipeline")
    p.add_argument("--date", required=True, help="Date in YYYY-MM-DD")
    p.add_argument("--dev", action="store_true", help="Run in development mode")
    p.set_defaults(func=lambda args: run_pipeline(args.date, args.dev))

    r = sub.add_parser("roi", help="Run ROI pipeline")
    r.add_argument("--date", required=True, help="Date in YYYY-MM-DD")
    r.add_argument("--dev", action="store_true", help="Run in development mode")
    r.set_defaults(func=lambda args: run_roi_pipeline(args.date, args.dev))

    s = sub.add_parser("sniper", help="Generate and schedule sniper jobs")
    s.add_argument("--dev", action="store_true", help="Run in development mode")
    s.set_defaults(func=lambda args: run_sniper_schedule(args.dev))

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
