import argparse
import shutil
from pathlib import Path
from datetime import datetime


def ensure_sent_tips(date: str,
                     predictions_dir: Path = Path('predictions'),
                     dispatch_dir: Path = Path('logs/dispatch')) -> Path | None:
    """Ensure sent tips file exists by copying from predictions if missing."""
    predictions_file = predictions_dir / date / 'tips_with_odds.jsonl'
    sent_file = dispatch_dir / f'sent_tips_{date}.jsonl'

    if sent_file.exists():
        print(f"✅ Sent tips already present: {sent_file}")
        return sent_file

    if not predictions_file.exists():
        print(f"❌ Missing predictions: {predictions_file}")
        return None

    dispatch_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(predictions_file, sent_file)
    print(f"📄 Created {sent_file} from predictions")
    return sent_file


def main() -> None:
    parser = argparse.ArgumentParser(description='Ensure sent tips file exists')
    parser.add_argument('--date', default=datetime.now().strftime('%Y-%m-%d'))
    parser.add_argument('--predictions-dir', default='predictions')
    parser.add_argument('--dispatch-dir', default='logs/dispatch')
    args = parser.parse_args()

    ensure_sent_tips(
        args.date,
        Path(args.predictions_dir),
        Path(args.dispatch_dir)
    )


if __name__ == '__main__':
    main()
