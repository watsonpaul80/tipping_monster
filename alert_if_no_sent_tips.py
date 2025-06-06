import argparse
from datetime import datetime
from pathlib import Path


def alert_if_no_sent_tips(date: str,
                          sent_dir: Path = Path('logs/dispatch'),
                          alert_log: Path = Path('logs/alerts/no_tips.log')) -> bool:
    """Log an alert if the sent_tips file is missing or empty."""
    sent_file = sent_dir / f'sent_tips_{date}.jsonl'
    if not sent_file.exists() or sent_file.stat().st_size == 0:
        alert_log.parent.mkdir(parents=True, exist_ok=True)
        with alert_log.open('a') as fh:
            fh.write(f"{date} NO_TIPS\n")
        print(f"⚠️ No tips dispatched for {date}")
        return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description='Alert if no tips were sent')
    parser.add_argument('--date', default=datetime.now().strftime('%Y-%m-%d'))
    parser.add_argument('--alert-log', default='logs/alerts/no_tips.log')
    args = parser.parse_args()
    alert_if_no_sent_tips(args.date, alert_log=Path(args.alert_log))


if __name__ == '__main__':
    main()
