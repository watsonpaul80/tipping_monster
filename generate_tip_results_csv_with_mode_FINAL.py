
import argparse
from datetime import datetime
import os
import pandas as pd

# Adjust as needed
LOGS_DIR = "logs"
TODAY = datetime.today().strftime("%Y-%m-%d")

# Dummy loading logic – replace with your actual tip/result merging logic
def load_tips_results(date_str: str):
    """Load the merged tips/results file for the given date."""
    return pd.read_csv(os.path.join(LOGS_DIR, f"tips_results_raw_{date_str}.csv"))

def calculate_level_stakes(row):
    odds = row["odds"]
    result = row["result"]
    bet_type = row["bet_type"]

    if bet_type == "each_way" or (bet_type == "win" and odds >= 5.0):
        # Treat as 1pt Win + 1pt Place = 2pts total staked
        win_profit = (odds - 1.0) if result == "won" else -1.0
        place_profit = (odds / 5.0 - 1.0) if result in ["won", "placed"] else -1.0
        total_stake = 2.0
        profit = win_profit + place_profit
    else:
        # Standard 1pt Win bet
        profit = (odds - 1.0) if result == "won" else -1.0
        total_stake = 1.0

    return pd.Series([total_stake, profit])

def main(date_str: str, mode: str):
    df = load_tips_results(date_str)

    df[["level_stake", "level_profit"]] = df.apply(calculate_level_stakes, axis=1)

    # Save cleaned file
    output_file = os.path.join(LOGS_DIR, f"tips_results_{date_str}_{mode}.csv")
    df.to_csv(output_file, index=False)
    print(f"✅ Level stakes file saved: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--date",
        default=TODAY,
        help="Date in YYYY-MM-DD format (default: today)",
    )
    parser.add_argument(
        "--mode",
        choices=["advised", "level"],
        default="level",
        help="ROI mode used for the output file name",
    )
    args = parser.parse_args()

    main(args.date, args.mode)
