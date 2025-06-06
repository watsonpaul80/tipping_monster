
import os
from pathlib import Path
import pandas as pd
from datetime import datetime

# === CONFIG ===
REPO_ROOT = Path(os.getenv("TM_ROOT", Path(__file__).resolve().parent))
LOG_DIR = REPO_ROOT / "logs"
OUT_DIR = LOG_DIR / "weekly_summaries"
os.makedirs(OUT_DIR, exist_ok=True)

# === GROUP FILES ===
files = [f for f in os.listdir(LOG_DIR) if f.startswith("tips_results_") and f.endswith(".csv")]
weekly_map = {}

for f in files:
    try:
        date_part = f.replace("tips_results_", "").replace(".csv", "")
        if "_" in date_part:
            date_str, mode = date_part.rsplit("_", 1)
        else:
            continue
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        iso_year, iso_week, _ = date_obj.isocalendar()
        key = f"{iso_year}-W{iso_week:02d}"
        weekly_map.setdefault(key, []).append(os.path.join(LOG_DIR, f))
    except:
        continue

# === MERGE BY WEEK ===
for week, file_list in weekly_map.items():
    dfs = []
    for f in file_list:
        df = pd.read_csv(f)
        dfs.append(df)
    if not dfs:
        continue
    df_all = pd.concat(dfs, ignore_index=True)
    for col in ["Valid Winner", "Valid EW Place"]:
        if col in df_all.columns:
            df_all[col] = df_all[col].replace("✅", "Yes")
    out_file = os.path.join(OUT_DIR, f"weekly_summary_{week}.csv")
    df_all.to_csv(out_file, index=False)
    print(f"✅ Exported: {out_file}")
