
## 2025-06-08

### Added
- Rolling 30-day ROI line chart in Paul's View dashboard.

### Documentation
- Updated monster_todo.md with newly completed tasks.

## 2025-06-20

### Added
- `generate_lay_candidates.py` identifies Danger Fav lay candidates.
- `dispatch_danger_favs.py` formats and sends Danger Fav alerts.
- `track_lay_candidates_roi.py` computes lay ROI for Danger Favs.

## 2025-06-08

### Added
- `telegram_bot.py` with `/roi` command to send ROI summaries.
=======

## 2025-06-08

### Fixes
- Removed stray `pip install model_drift_report` from the GitHub workflow, relying on the local module instead.

## 2025-06-17

### Added
- `utils/band_roi_filter.py` with `is_band_profitable()` helper.
=======

## 2025-06-17

### Added
- Streamlit dashboard now includes an ROI Summary table with a CSV download button.

## 2025-06-17

### Added
- New `generate_weekly_roi.py` script creates weekly ROI CSVs in `logs/weekly_summaries/`.

## 2025-06-19

### Added
- Streamlit dashboard now includes sidebar checkboxes to filter the Full Tip
  Breakdown for winners or placed horses.



## 2025-06-13

### Changed
- Centralized each-way place term logic in `tippingmonster.utils.get_place_terms()`.
- ROI trackers now import this helper instead of defining it locally.

### Removed
- Deleted `tipping-monster-xgb-model.bst` from the repository. Tests now
  generate a temporary XGBoost model instead.

## 2025-06-16

### Added
- `dispatch_tips.py` skips tips below 0.80 confidence unless their confidence
  band has shown positive ROI in the past 30 days.

## 2025-06-17

### Fixed
- `test_model_drift` now verifies SHAP files exist and uses a stable datetime
  override to prevent `FileNotFoundError`.

## 2025-06-15

### Changed
- `generate_unified_roi_sheet.py` now merges ROI CSVs from any year.

## 2025-06-14

### Changed
- Removed lightweight model binary from the repository. Unit tests now build a
  temporary XGBoost model instead.

## 2025-06-13

### Fixed
- Added missing `requests` import in `roi/weekly_roi_summary.py`.

## 2025-06-13

### Fixed
- Added missing `requests` import in `roi/weekly_roi_summary.py`.

## 2025-06-12

### Fixed
- `load_shap_csv()` now deletes the downloaded temp file after reading.
- Removed duplicate `requests` entry from `requirements.txt`.
- Added missing `send_telegram_message` import in `dispatch_all_tips.py`.

## 2025-06-10

### Fixed
- Added missing `requests` import in `scripts/morning_digest.py` so Telegram posts work.

## 2025-06-11

### Added
- New `tip_has_tag()` helper in `tippingmonster.utils` for tag substring checks.

## 2025-06-12

### Fixed
- Removed duplicate `tip_has_tag` entry from `tippingmonster.__all__`.

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
- `load_shap_csv` now removes temporary S3 downloads after reading to avoid clutter.

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