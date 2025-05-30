# 🔫 Steam Sniper Mode Overview

## Purpose
Automatically detect horses whose betting odds are dropping sharply (≥30%) in the run-up to a race, even if they weren’t tipped earlier — then send high-quality, context-rich alerts to Telegram subscribers.

## How It Works — Step by Step

1. **Fetch odds snapshots** at key times:  
   - Baseline at 08:00  
   - Then at T-60, T-30, T-10 minutes before each race start  

2. **Collect volume matched** on Betfair alongside odds, to gauge market interest  

3. **Merge snapshots** for each horse to create a timeline of odds progression and volume (e.g., 28/1 → 18/1 → 12/1 → 8/1)  

4. **Detect steamers**:  
   - Identify horses where odds have dropped ≥30% compared to 08:00  
   - Attach volume data and optionally confidence tiers or form overlays  

5. **Dispatch alerts to Telegram**:  
   - Format alerts with odds progression, volume, race, horse name, and optionally trainer form and confidence  
   - Send in batches of 5 messages to avoid flooding  

## Core Scripts Used

| Script Name                       | Purpose                                                                                   |
|------------------------------------|------------------------------------------------------------------------------------------|
| `fetch_betfair_sniper_odds.py`     | Fetch odds and matched volume snapshots from Betfair at specified times, save JSON files  |
| `merge_sniper_history.py`          | Combine daily snapshots into per-horse odds progression and volume timelines              |
| `detect_and_save_steamers.py`      | Analyze merged data, detect ≥30% odds drops, create filtered steamer JSON for dispatch    |
| `dispatch_snipers.py`              | Format and send sniper alerts to Telegram based on steamer JSON data                      |
| `build_sniper_schedule.py`         | Generate daily snapshot schedule times based on race start times                          |
| `generate_and_schedule_snipers.sh` | Create `at` jobs to run sniper pipeline at scheduled snapshot times                       |
| `run_sniper_pipeline.sh`           | Master shell script to run fetch → merge → detect → dispatch for a given snapshot label   |
| `safecron.sh`                      | Wrapper for cron jobs with logging and Telegram failure alerts                            |

## Data Flow Summary

Racecards JSONL (daily batch) → build_sniper_schedule.py → schedule snapshot times  
↓  
fetch_betfair_sniper_odds.py (runs at snapshot times, saves odds+volume JSON)  
↓  
merge_sniper_history.py (daily merges snapshots into odds progression per horse)  
↓  
detect_and_save_steamers.py (detects steamers with ≥30% drop)  
↓  
dispatch_snipers.py (sends formatted alerts to Telegram)

## Useful Manual Commands

```bash
# Run full sniper pipeline for a snapshot label
bash run_sniper_pipeline.sh 1420

# Build daily sniper snapshot schedule
python build_sniper_schedule.py

# Schedule sniper jobs with at
bash generate_and_schedule_snipers.sh

# Detect steamers manually
python detect_and_save_steamers.py --date 2025-05-28 --label 1420

# Dispatch sniper alerts
python dispatch_snipers.py --source sniper_data/steamers_2025-05-28_1420.json

# Monitor logs
tail -f logs/build_sniper_intel_$(date +%F).log
tail -f logs/load_sniper_intel_$(date +%F).log
```

---

## 🧠 Detection Logic

- Steamers are runners with a **≥30% odds drop** from the initial snapshot.
- Odds snapshots are taken at: **08:00**, **T-60**, **T-30**, and **T-10** mins before off time.
- Only WIN market odds from Betfair are considered.
- Volume matched data is also captured but currently not used in filter logic.

---

## 🔁 Workflow Summary

1. **Build the Race Schedule:**  
   `build_sniper_schedule.py` pulls all races for the day with times.

2. **Generate Jobs to Fetch Odds:**  
   `generate_and_schedule_snipers.sh` uses the race times to create `at` jobs for each snapshot point (T-60, T-30, T-10).

3. **Run Snapshot Pipeline:**  
   Each scheduled job executes:
   - `fetch_betfair_sniper_odds.py`: grabs Betfair odds for all GB/IRE runners
   - `merge_sniper_history.py`: creates timeline of odds per runner
   - `detect_and_save_steamers.py`: flags drops ≥30%
   - `dispatch_snipers.py`: formats and sends Telegram alert

---

## 📂 File Output

- `steam_sniper_intel/sniper_data/` — odds snapshots (labelled by time)
- `steam_sniper_intel/merged_*.json` — timeline of odds movement
- `steam_sniper_intel/steamers_*.json` — confirmed steamers with metadata

---

## 📨 Telegram Output Format

```
🔥 Steam Sniper: Market Intelligence
📍 14:20 York
🐎 Al Ameen
🔻 Odds Drop: 20/1 → 16/1 → 10/1 → 6/1
💰 Volume: £2,134 matched
```

- Only 5 are sent per batch to avoid spam.
- Steamer data includes all drops from 08:00 and any previous snapshots.

---

## 📋 Future Improvements

- Add confidence filter from ML model (e.g. only show if >25% chance)
- Score steamers using trends, trainer/jockey form, class drop, etc.
- Add charts or emojis to show trend intensity
- Telegram suppression for weak steamers

---