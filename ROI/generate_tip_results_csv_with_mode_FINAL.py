
import pandas as pd
import os
from datetime import datetime

# Adjust as needed
LOGS_DIR = "logs"
TODAY = datetime.today().strftime("%Y-%m-%d")

# Dummy loading logic – replace with your actual tip/result merging logic
def load_tips_results():
    # Expecting a dataframe with: horse, result, odds, bet_type
    return pd.read_csv(f"{LOGS_DIR}/tips_results_raw_{TODAY}.csv")

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
    df = load_tips_results()

    df[["level_stake", "level_profit"]] = df.apply(calculate_level_stakes, axis=1)

    # Save cleaned file
    output_file = f"{LOGS_DIR}/tips_results_{TODAY}_level.csv"
    df.to_csv(output_file, index=False)
    print(f"✅ Level stakes file saved: {output_file}")

if __name__ == "__main__":
    main()
