# 🔫 Steam Sniper Mode Overview (Updated – 31 May 2025)

## 🎯 Purpose
Automatically detect horses whose **Betfair odds have dropped ≥30%** during the day — even if they weren’t tipped — and **send sharp, clean alerts** to Telegram subscribers as a signal of major market movement ("Steamers").

---

## ⚙️ How It Works — Step by Step

1. **Fetch odds snapshots** at multiple times:
   - First snapshot is **08:00**
   - Then snapshot at **T-60, T-30, T-10 mins** before race start

2. **Save odds snapshots** as JSON files in `steam_sniper_intel/sniper_data/`, tagged by label (e.g. `1505` for 15:05)

3. **Detect steamers:**
   - Compare most recent snapshot to earliest (usually 08:00)
   - Flag any runner whose price has dropped **≥30%**
   - ✅ *No longer requires volume thresholds due to Betfair API limits*

4. **Save results** to `steamers_YYYY-MM-DD_HHMM.json`

5. **Dispatch to Telegram:**
   - Format odds drops (e.g., 18/1 → 12/1 → 8/1)
   - Send alert in a human-readable batch of up to 10 steamers per message

---

## 📜 Core Scripts Used

| Script | Purpose |
|--------|---------|
| `fetch_betfair_sniper_odds.py` | Fetch odds snapshots for all runners in GB/IRE WIN markets |
| `compare_sniper_odds.py` | Detect steamers by comparing current snapshot to the earliest |
| `dispatch_snipers.py` | Format and send steamer alerts to Telegram |
| `build_sniper_schedule.py` | Builds the list of snapshot times per race |
| `generate_and_schedule_snipers.sh` | Schedules all fetch jobs using `at` commands |
| `run_sniper_pipeline.sh` | Runs fetch → detect → dispatch in one step |
| `safecron.sh` | Runs cron jobs safely with logging and Telegram error alerts |

---

## 🔁 Workflow Summary

1. `build_sniper_schedule.py`  
   ⮕ Generates snapshot times (e.g. `0930`, `1005`, `1020`)

2. `generate_and_schedule_snipers.sh`  
   ⮕ Schedules `run_sniper_pipeline.sh LABEL` for each snapshot label

3. `run_sniper_pipeline.sh 1505`  
   ⮕ Runs:
   - `fetch_betfair_sniper_odds.py` → saves `1505.json`
   - `compare_sniper_odds.py` → compares to 08:00 and saves `steamers_1505.json`
   - `dispatch_snipers.py` → sends to Telegram

---

## 📂 File Structure & Output

| Folder / File | Description |
|---------------|------------|
| `steam_sniper_intel/sniper_data/` | Snapshot odds files (`HHMM.json`) |
| `steam_sniper_intel/sniper_data/steamers_*.json` | Final output — list of confirmed steamers |
| `sniper_schedule.txt` | Times like `0930`, `0950`, etc. |

---

## ✉️ Telegram Alert Format

🔥 **Steam Sniper Alert**  
📍 **14:20 Chester**  
🐎 **William Walton**  
🔻 **Odds Drop: 20/1 → 14/1 → 8/1**  

- No volume attached anymore  
- If ML scoring added later, confidence tiers can be included  

---

## 🛠️ Useful Manual Commands

```bash
# Run pipeline for specific label (e.g. 1505)
bash run_sniper_pipeline.sh 1505

# Compare odds manually
python compare_sniper_odds.py --snapshot steam_sniper_intel/sniper_data/2025-05-31_1505.json --label 1505

# Send steamer alerts manually
python dispatch_snipers.py --source steam_sniper_intel/sniper_data/steamers_2025-05-31_1505.json

# Build today’s snapshot schedule
python build_sniper_schedule.py

# Schedule the snapshots for today
bash generate_and_schedule_snipers.sh
🧠 Detection Logic
Steamer = any runner whose odds dropped ≥30%

Based on comparing current odds to earliest snapshot

Volume was removed (Betfair doesn't support it in bulk API)

🚀 Improvements on the Horizon
🧠 Add ML scoring for steamer confidence 📉 Display odds history progression with emojis/arrows 📊 Detect drifters as well (odds rising) 🕐 Use snapshots like 1 hour before, 30 mins before, 10 mins before