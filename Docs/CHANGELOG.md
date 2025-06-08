# 📅 CHANGELOG

## 2025-06-12

### Fixed
- Removed duplicate `requests` entry from `requirements.txt`.

## 2025-06-10

### Fixed
- Added missing `requests` import in `scripts/morning_digest.py` so Telegram posts work.

## 2025-06-11

### Added
- New `tip_has_tag()` helper in `tippingmonster.utils` for tag substring checks.

## 2025-06-09
- Moved pipeline and ROI scripts into `core/`, `roi/`, and `utils/` directories. Updated docs and README references.

### Added
- NAP odds cap with override support (`dispatch_tips.py`).
- Blocked or reassigned NAPs logged to `logs/nap_override_YYYY-MM-DD.log`.
- NAP removed entirely when no tip meets the cap, with log entry noted.
- Optional SHAP chart upload added in `model_feature_importance.py`.
- `roi_tracker_advised.py` and `tag_roi_tracker.py` now accept `--tag` to filter tips by tag substring.
- Removed duplicate arguments and calculations in `tag_roi_tracker.py`.
- Added `--dev` option.

## 2025-06-08

### Added
- `model_drift_report.py` generates a markdown summary highlighting SHAP feature drift.
- `roi_by_confidence_band.py` aggregates tip ROI by confidence band and writes `logs/roi/roi_by_confidence_band_*.csv`.
- `cli/tmcli.py` now supports `dispatch-tips` and `send-roi` commands for one-line Telegram posts.

- `validate_features.py` wraps `core.validate_features` for backward compatibility.


## 2025-06-07

### Added
- NAP odds cap with override support (`dispatch_tips.py`).
- Blocked or reassigned NAPs logged to `logs/nap_override_YYYY-MM-DD.log`.
- NAP removed entirely when no tip meets the cap, with log entry noted.
- `validate_tips.py` for verifying tips files before dispatch.
- Added unit tests for `tmcli` subcommands.
- Added unit test for `roi_by_confidence_band.summarise`.
- ROI trackers now support `--tag` filtering for NAP/Value tips.

## 2025-06-07 — Script Cleanup

- Added `script_audit.txt` listing unused scripts.
- Document now referenced in README files.

## 2025-06-07 — CLI Helper


- Added `cli/tmcli.py` with `pipeline`, `roi`, `sniper`, and `healthcheck` subcommands.
- Each command supports a `--dev` flag for safe local testing.
- Documented CLI usage in README and ops guide.

## 2025-06-06 — ROI Script Consolidation

- Removed duplicate scripts from `ROI/` directory.
- Canonical versions kept in project root.

## 2025-06-01 — ROI Tracker Fixes

### Tipping Monster Core
- Fixed ROI tracker not running via cron due to incorrect default date logic.
- Manual ROI run for 2025-05-31 completed:
  - Profit: -1.00 pts | ROI: -7.69% | Stake: 13.00 pts
- `send_daily_roi_summary.py` tested manually and confirmed working when correct `--date` used.
- Diagnosis: ROI script defaulted to today even when `--date` was passed (issue still under review).

---

## 2025-05-31 — ROI Accuracy Overhaul + Pipeline Simplification

### ROI & Place Logic Fixes
- Updated `roi_tracker_advised.py` to correctly calculate each-way (EW) place profit.
- Handles 1/4 and 1/5 odds fractions with full/half stake logic.
- Flags placed horses and applies correct payouts based on position.

### Best Odds Integration
- Fully integrated `extract_best_realistic_odds.py` into nightly pipeline.
- Ensures accurate profit tracking for both win and place legs.
- Backfilled recent tips using realistic odds.

### Cron Simplification
- Created `run_roi_pipeline.sh` to consolidate 4 cron jobs into 1:
  - Realistic odds injection
  - Advised & level ROI tracking
  - Telegram summary dispatch

### Summary Enhancements
- `weekly_roi_summary.py` now includes 🥈 places.
- Improved formatting for Telegram output.
- `send_daily_roi_summary.py` supports `--show` for local CLI testing.

---

## [2025-05-31] 🔫 Steam Sniper V1 — Stable Launch

### Major Fixes
- Fixed issue where sniper jobs failed due to early race schedule.
- Cron now builds sniper schedule at 09:30 (after racecards are ready).
- Odds parsing supports both `3:15` and `15:15` formats.

### Core Features Completed
- Automated snapshot scheduling based on race times.
- Dynamic odds snapshot merging and formatting (`20/1 → 10/1 → 7/1`).
- Past races filtered out from alerts.
- Volume filtering removed due to Betfair limits.
- Telegram batches alerts in groups of 20.

### New Files / Scripts
- `compare_sniper_odds.py` replaces old snapshot logic.

### Next Up
- ROI tracking for steamers
- LLM commentary
- ML-based filtering in V2

---

## [2025-05-31] 🧠 Tipping Monster — Pipeline Stability & Odds Snapshot Cleanup

### Fixes & Enhancements
- Standardized `compare_odds_to_0800.py` across subsystems.
- Deprecated legacy `odds_snapshots/` folder.
- Snapshot loader now finds earliest available file, not just 08:00.

### Testing & Validation
- Verified full odds snapshot → comparison → steamer flow.

---