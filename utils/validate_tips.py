import argparse
import json
from datetime import datetime
from pathlib import Path

REQUIRED_FIELDS = ["name", "race", "confidence"]


def validate_tips(date: str, predictions_dir: Path = Path("predictions")) -> bool:
    """Return True if all tips for ``date`` contain required fields."""
    tips_file = predictions_dir / date / "tips_with_odds.jsonl"
    if not tips_file.exists():
        print(f"\u274c Tips file missing: {tips_file}")
        return False

    all_valid = True
    with tips_file.open("r", encoding="utf-8") as fh:
        for idx, line in enumerate(fh, start=1):
            try:
                tip = json.loads(line)
            except json.JSONDecodeError:
                print(f"\u274c Invalid JSON on line {idx}")
                all_valid = False
                continue
            for field in REQUIRED_FIELDS:
                if field not in tip:
                    print(f"\u274c Missing '{field}' on line {idx}")
                    all_valid = False
    if all_valid:
        print("\u2705 Tips file valid")
    return all_valid


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="Validate tips JSON file")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("--predictions-dir", default="predictions")
    args = parser.parse_args(argv)
    validate_tips(args.date, Path(args.predictions_dir))


if __name__ == "__main__":
    main()
