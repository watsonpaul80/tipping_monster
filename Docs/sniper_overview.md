# 🔫 Steam Sniper Mode Overview

## Purpose
Automatically detect and dispatch horses whose Betfair odds drop sharply (≥30%) leading up to a race, regardless of whether they were previously tipped.

## Key Concepts
- **Steamers** = Horses with significant odds drops (≥30%)
- **Snapshots** = Time-based captures of Betfair odds
- **Schedule** = Timed sniper jobs that fetch odds and dispatch alerts

---

## 🧠 How It Works – Step by Step

### 1. ⏱️ Build Snapshot Schedule
- Uses today's `rpscrape/batch_inputs/YYYY-MM-DD.jsonl` racecard file
- Extracts race times from `"race"` field (e.g. `"17:15 Chelmsford"`)
- Applies snapshot offsets (T-60, T-30, T-10) to calculate capture points
- Output: `steam_sniper_intel/sniper_schedule.txt`

### 2. 🕐 Schedule Jobs
- `run_sniper_pipeline.sh` loops through `sniper_schedule.txt`
- Each time is registered via `at` command to run sniper + dispatch

### 3. 📸 Fetch Odds Snapshot
- At each scheduled time, `fetch_betfair_odds.py --label TIME` is triggered
- Snapshot JSON is saved under `odds_snapshots/YYYY-MM-DD_HHMM.json`

### 4. 🔎 Compare to Baseline
- `compare_odds_to_0800.py` compares latest snapshot to `08:00` snapshot
- Horses with ≥30% odds drops are marked as steamers

### 5. 📤 Dispatch Steamers
- `dispatch_snipers.py` sends formatted steamer alerts to Telegram
- Each message is capped to 20 runners to avoid spam
- Dispatches include emoji indicators and confidence tiers (future)

---

## 🛠️ Cron Setup

```cron
# 1. Build sniper schedule (after racecards are ready)
5 8 * * * /home/ec2-user/tipping-monster/.venv/bin/python /home/ec2-user/tipping-monster/steam_sniper_intel/build_sniper_schedule.py

# 2. Launch pipeline jobs via `at`
6 8 * * * /home/ec2-user/tipping-monster/steam_sniper_intel/run_sniper_pipeline.sh
📂 Key Files
| File | Purpose |
| ---- | ------- |
| build_sniper_schedule.py | Generates snapshot times from racecard |
| run_sniper_pipeline.sh | Schedules fetch/dispatch jobs via at |
| fetch_betfair_odds.py | Captures odds snapshots |
| compare_odds_to_0800.py | Finds steamers vs baseline |
| sniper_schedule.txt | List of HHMM-formatted snapshot times |
| odds_snapshots/*.json | Raw odds snapshots |
| steamers_*.json | Steamers detected at each timepoint |

✅ Example Flow
08:00 →  build_sniper_schedule.py
08:01 →  run_sniper_pipeline.sh
12:55 →  fetch_betfair_odds.py --label 1255
12:55 →  compare_odds_to_0800.py
```

---

## 📝 Changelog Entry (`TIPPING_MONSTER_CHANGELOG.md`)

```md
## [2025-06-01] Steam Sniper Pipeline Overhaul ✅

### ➕ Features Added
- Fully dynamic snapshot scheduling using actual racecard times
- `build_sniper_schedule.py` now extracts race times from JSONL file
- Auto-adjusts for only future snapshots (filters out past)
- `run_sniper_pipeline.sh` reads schedule and registers timed `at` jobs

### 🛠️ Fixes & Improvements
- Fixed issue where schedule defaulted to just `08:50` if race times unreadable
- Improved time parsing from `"race"` field (e.g. “17:15 Chelmsford”)
- Verified pipeline now triggers dispatches for full race day
- Added future-proofing for early and late race times.
```
