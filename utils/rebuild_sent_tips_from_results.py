import json
import pandas as pd
from pathlib import Path

RESULTS_DIR = Path("logs")
OUT_DIR = RESULTS_DIR


def find_result_files():
    return sorted(RESULTS_DIR.glob("tips_results_2025-05-*.csv"))


def convert_to_jsonl(df, date, output_path):
    fields = [
        "Date", "Track", "Time", "EW/Win", "Jockey", "Horse", "Odds",
        "Best Odds", "Confidence", "Result", "Staked", "Profit",
        "Running Profit", "Running Profit Best Odds", "Trainer", "Tags"
    ]
    df["Date"] = date
    df["Tags"] = ""  # Backfill empty tags
    df["Trainer"] = df.get("Trainer", "Unknown")  # Optional trainer fallback

    with open(output_path, "w") as f:
        for _, row in df.iterrows():
            tip = {k: row.get(k, None) for k in fields}
            f.write(json.dumps(tip) + "\n")
    print(f"✅ Wrote: {output_path}")


def backfill_all():
    for file in find_result_files():
        date_str = file.stem.split("_")[2]
        output_path = OUT_DIR / f"sent_tips_{date_str}.jsonl"
        if output_path.exists():
            print(f"⚠️ Already exists: {output_path}")
            continue
        df = pd.read_csv(file)
        convert_to_jsonl(df, date_str, output_path)


if __name__ == "__main__":
    backfill_all()
