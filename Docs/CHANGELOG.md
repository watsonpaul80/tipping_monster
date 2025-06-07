# 📅 CHANGELOG

## 2025-06-08

### Added
- `model_drift_report.py` generates a markdown summary highlighting SHAP feature drift.

## 2025-06-07

### Added
- NAP odds cap with override support (`dispatch_tips.py`).
- Blocked or reassigned NAPs logged to `logs/nap_override_YYYY-MM-DD.log`.
- NAP removed entirely when no tip meets the cap, with log entry noted.
- Added unit tests for `tmcli` subcommands.
- ROI trackers now support `--tag` filtering for NAP/Value tips.


## 2025-05-31

### Added

### Fixed
-- Schedule builder now avoids empty output silently

### Changed
- All scheduled snapshot jobs now log job ID + time in output


## [2025-05-31] 🔫 Steam Sniper V1 — Stable Launch

### ✅ Major Fixes
- Fixed critical issue where sniper jobs failed due to early race schedule creation.
- Updated cron to build sniper schedule at 09:30 (after racecards are ready).
- Fallback parsing for both `3:15` and `15:15` time formats in racecards.

### ✅ Core Features Completed
- Fully automated snapshot scheduling and fetching based on race times.
- Snapshot comparison now dynamically finds earliest available file (not just 08:00).
- Odds progression shown in clean format: `20/1 → 10/1 → 7/1`.
- Past races filtered out from dispatch automatically.
- Volume filtering removed due to Betfair API call limits.
- Telegram dispatch batches alerts in groups (up to 20) with dryrun support.

### 🧪 Manual Testing
- Dry-run mode added for safe CLI output testing.
- Successfully tested full sniper pipeline: fetch → merge → detect → dispatch.

### 📂 New Files / Scripts
- `compare_sniper_odds.py`: Replaces old snapshot comparison logic.

### 🏼 Next Up
- ROI tracking for steamers
- LLM commentary
- ML-based filtering in V2

## [2025-05-31] 🧠 Tipping Monster — Pipeline Stability & Odds Snapshot Cleanup

### ✅ Fixes & Enhancements
-- Standardized `compare_odds_to_0800.py` logic across systems.
-- Clarified snapshot folder usage:
  - Legacy snapshots: `odds_snapshots/`
- Deprecated old snapshot folder (`odds_snapshots/`) for main system use.
- Fixed bug where `compare_odds_to_0800.py` would fail if the given snapshot didn’t exist.
- Snapshot loader now finds **earliest available odds snapshot of the day**, even if not exactly 08:00.

### 🧪 Testing & Validation
- Verified clean pipeline execution for odds comparison using latest snapshot labels.
- Confirmed consistent behaviour in cases with and without early snapshot data.

### 📂 Structure Cleanup
- Refined script calls so that odds comparisons and steamer detection are cleanly separated.
- Ensured proper `Path()`-based handling and errors in missing snapshot cases.

---

Let me know if you want it appended to your existing Monster changelog file or injected into the `TIPPING_MONSTER_OVERVIEW.md` or `TIPPING_MONSTER_TODO.md`.

## [2025-05-31] Tipping Monster ROI Tracker Fixes

- ROI tracking now correctly handles both daily and weekly summaries.
- Fixed safe numeric conversion of Profit and Stake (coercing and filling NaNs).
- Daily logs (`tips_results_YYYY-MM-DD_advised.csv`) now feed into weekly summaries.
- Added `weekly_roi_summary.py` for Telegram-ready summaries and audits.
- Added `generate_weekly_summary.py` to consolidate all logs per ISO week.
- Telegram output supports inline summaries and detailed daily breakdowns.


## 🗓️ 2025-05-31 — ROI Accuracy Overhaul + Pipeline Simplification

### ✅ ROI & Place Logic Fixes
- Updated `roi_tracker_advised.py` to correctly calculate each-way (EW) place profit.
  - Dynamically determines place terms based on runners & race type.
  - Handles 1/4 and 1/5 odds fractions with full/half stake logic.
  - Flags placed horses and applies correct payouts based on position.
- Rebuilt May 30 results with corrected place earnings.
- Confirmed correct place detection & profit application in win/place splits.

### 📈 Best Odds Integration
  - Fully integrated `extract_best_realistic_odds.py` into nightly pipeline.
- Ensures accurate profit tracking for both win and place legs.
- Backfilled recent tips (e.g., May 30) using realistic odds.

### 🧼 Cron Simplification
  - Created `run_roi_pipeline.sh` to consolidate 4 cron jobs into 1:
    - Realistic odds injection
    - Advised & level ROI tracking
    - Telegram summary dispatch
  - All ROI-related logs now stored in `logs/roi/` for tidiness.

### 📊 Weekly & Daily Summary Enhancements
- `weekly_roi_summary.py` updated to include:
  - Place count (🥈)
  - Improved formatting for Telegram summary
- `send_daily_roi_summary.py` now shows:
  - 🏇 Tips, 🥇 Wins, 🥈 Places, 📈 ROI, and 💰 Profit
- Added `--show` mode to support local CLI use without Telegram.

---

# 🧾 TIPPING MONSTER — MASTER CHANGELOG

## 📅 2025-06-01


### 🧠 Tipping Monster Core

- 🛠️ Fixed ROI tracker not running via cron due to incorrect default date logic
- ✅ Manual ROI run for 2025-05-31 completed:
  - Profit: -1.00 pts | ROI: -7.69% | Stake: 13.00 pts
- ✅ `send_daily_roi_summary.py` tested manually and confirmed working when correct `--date` used
- 🔍 Diagnosis: ROI script defaulted to today even when `--date` was passed (issue still under review)

---
## 2025-06-06 — ROI Script Consolidation
- Removed duplicate scripts from `ROI/` directory.
- Canonical versions kept in project root.


## 2025-06-07 -- Script Cleanup
- Added script_audit.txt listing unused scripts
- Document now referenced in README files

## 2025-06-07 — CLI Helper
- Added `tmcli.py` with `pipeline`, `roi`, `sniper` and `healthcheck` subcommands.
- Each command supports a `--dev` flag for safe local testing.
- Documented CLI usage in README and ops guide.
## 2025-06-08

### Added
- `roi_by_confidence_band.py` aggregates tip ROI by confidence band and writes `logs/roi/roi_by_confidence_band_*.csv`.

## 2025-06-08 — Telegram CLI
- `tmcli.py` now supports `dispatch-tips` and `send-roi` commands for one-line
  Telegram posts.


