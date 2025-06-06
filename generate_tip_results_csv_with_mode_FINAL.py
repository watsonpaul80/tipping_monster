
import argparse
import pandas as pd
import os
from datetime import datetime

# Adjust as needed
LOGS_DIR = "logs"

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--date",
        default=datetime.today().strftime("%Y-%m-%d"),
        help="Date in YYYY-MM-DD",
    )
    parser.add_argument("--mode", choices=["advised", "level"], required=True)
    return parser.parse_args()

# Dummy loading logic – replace with your actual tip/result merging logic
def load_tips_results(date_str: str) -> pd.DataFrame:
    """Load merged tips and results for the given date."""
    return pd.read_csv(f"{LOGS_DIR}/tips_results_raw_{date_str}.csv")

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

def main():
    args = parse_args()
    df = load_tips_results(args.date)

    df[["level_stake", "level_profit"]] = df.apply(calculate_level_stakes, axis=1)

    # Save cleaned file
    output_file = f"{LOGS_DIR}/tips_results_{args.date}_{args.mode}.csv"
    df.to_csv(output_file, index=False)
    print(f"✅ Level stakes file saved: {output_file}")

if __name__ == "__main__":
    main()
