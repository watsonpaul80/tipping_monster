import os
import pandas as pd
from glob import glob

OUTPUT_PATH = "logs/roi/unified_roi_sheet.csv"


def load_and_flag(path, sent=False):
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path)
    df["sent"] = sent
    return df


def main():
    all_files = sorted(glob("logs/roi/tips_results_2025-*-advised.csv"))
    merged_rows = []

    for all_path in all_files:
        sent_path = all_path.replace("_advised.csv", "_advised_sent.csv")

        df_all = load_and_flag(all_path, sent=False)
        df_sent = load_and_flag(sent_path, sent=True)

        if not df_all.empty:
            if not df_sent.empty:
                df_all.set_index(["race", "name"], inplace=True)
                df_sent.set_index(["race", "name"], inplace=True)
                df_all.update(df_sent)
                df_all.reset_index(inplace=True)
            merged_rows.append(df_all)

    if merged_rows:
        final_df = pd.concat(merged_rows, ignore_index=True)
        final_df.to_csv(OUTPUT_PATH, index=False)
        print(f"✅ Saved to {OUTPUT_PATH}")
    else:
        print("⚠️ No data found to merge.")


if __name__ == "__main__":
    main()
