## [2025-06-25] Add NAP performance tracker
**Prompt:** Create nap_tracker.py to log NAP results over time.
**Files Changed:** roi/nap_tracker.py, tests/test_nap_tracker.py, Docs/CHANGELOG.md, Docs/monster_todo.md, Docs/monster_overview.md, codex_log.md
**Outcome:** New script logs daily NAP ROI to nap_history.csv and can summarise weekly.


## [2025-06-25] Add band performance to ROI summaries
**Prompt:** Update weekly and daily ROI scripts to break down results by confidence band.
**Files Changed:** roi/weekly_roi_summary.py, roi/send_daily_roi_summary.py, Docs/CHANGELOG.md, codex_log.md
**Outcome:** ROI summaries now include per-band stats with emoji highlights and CSV logs.

## [2025-06-25] Add staking simulator
**Prompt:** Create `simulate_staking.py` to compare level, confidence, and value staking profiles.
**Files Changed:** simulate_staking.py, tests/test_simulate_staking.py, Docs/CHANGELOG.md, Docs/monster_overview.md, Docs/TIPPING_MONSTER_ROI_OVERVIEW.md, Docs/script_audit.txt, all_scripts.txt, codex_log.md
**Outcome:** New script outputs profit summaries and a profit curve chart.

## [2025-06-24] Add value_score tagging
**Prompt:** Codex, update inference to calculate a value_score = (confidence / bf_sp) * 100. Tag as 💰 Value Pick if score > 5. Log and send as normal tip with tag.
**Files Changed:** core/merge_odds_into_tips.py, core/dispatch_tips.py, tests/test_dispatch_tips.py, Docs/monster_overview.md, Docs/monster_todo.md, Docs/CHANGELOG.md, codex_log.md
**Outcome:** Tips now include a value_score field and are tagged "💰 Value Pick" when the score exceeds 5.

## [2025-06-24] Add rolling ROI script
**Prompt:** Compute 30-day rolling ROI from sent logs.
**Files Changed:** generate_rolling_roi.py, Docs/CHANGELOG.md, Docs/monster_todo.md, Docs/TIPPING_MONSTER_ROI_OVERVIEW.md, all_scripts.txt, codex_log.md
**Outcome:** New CSV logs daily and rolling ROI figures.


## [2025-06-24] Add public ROI dashboard
**Prompt:** Codex, build public_dashboard.py using Streamlit. Load _sent.csv files, show ROI charts and tag stats.
**Files Changed:** public_dashboard.py, all_scripts.txt, Docs/CHANGELOG.md, Docs/monster_todo.md, codex_log.md
**Outcome:** New dashboard visualises ROI from sent tips only.


## [2025-06-23] Log auto tweets in dev mode
**Prompt:** Before posting tweets, check `TM_DEV_MODE`.
**Files Changed:** monstertweeter/auto_tweet_tips.py, Docs/ops.md, Docs/quickstart.md, tests/test_auto_tweet_dev_mode.py, Docs/CHANGELOG.md, codex_log.md
**Outcome:** Tweets are written to `logs/dev/twitter.log` when `TM_DEV_MODE=1`.

## [2025-06-08] Fix README security review link
**Prompt:** Update README to reference Docs/SECURITY_REVIEW.md and verify Docs prefixes.
**Files Changed:** README.md, Docs/CHANGELOG.md, codex_log.md
**Outcome:** Fixed documentation link inconsistencies.


## [2025-06-22] Add tag ROI table to streamlit
**Prompt:** Codex, add a table to streamlit_pauls_view.py showing ROI, strike rate, and profit per tag.
**Files Changed:** streamlit_pauls_view.py, Docs/CHANGELOG.md, Docs/monster_todo.md, Docs/TIPPING_MONSTER_ROI_TODO.md, all_scripts.txt, codex_log.md
**Outcome:** Paul's dashboard now highlights top-performing tags.
## [2025-06-08] Remove invalid model_drift_report install
**Prompt:** Fix GitHub workflow failing because package `model_drift_report` is missing.
**Files Changed:** .github/workflows/python-tests.yml, Docs/CHANGELOG.md, codex_log.md
**Outcome:** Workflow now installs only standard dependencies and uses local module.

## [2025-06-20] Add Danger Fav candidate script
**Prompt:** Create generate_lay_candidates.py to flag favourites with low Monster confidence.
**Files Changed:** generate_lay_candidates.py, tests/test_generate_lay_candidates.py, Docs/CHANGELOG.md, Docs/monster_overview.md, Docs/TIPPING_MONSTER_PRODUCTS.md, all_scripts.txt, codex_log.md
**Outcome:** Script outputs Danger Fav candidates and accompanying test added.

## [2025-06-20] Add Danger Fav dispatch and ROI tracking
**Prompt:** Create dispatch_danger_favs.py, update dashboard with Danger Fav view, and add ROI tracker for lays.
**Files Changed:** dispatch_danger_favs.py, track_lay_candidates_roi.py, cli/streamlit_dashboard.py, Docs/CHANGELOG.md, Docs/monster_overview.md, Docs/TIPPING_MONSTER_PRODUCTS.md, all_scripts.txt, tests/test_track_lay_candidates_roi.py, codex_log.md
**Outcome:** Danger Fav alerts can be sent to Telegram and ROI tracking logic implemented.

## [2025-06-21] Export Danger Fav CSV summary
**Prompt:** Create export_lay_candidates_csv.py to convert danger_favs.jsonl to CSV.
**Files Changed:** export_lay_candidates_csv.py, all_scripts.txt, Docs/CHANGELOG.md, Docs/monster_overview.md, Docs/TIPPING_MONSTER_PRODUCTS.md, codex_log.md
**Outcome:** Users can easily view Danger Fav candidates in spreadsheet form.

## [2025-06-08] Completed TODO Audit
**Prompt:** Audit monster_todo.md and mark completed tasks.
**Files Changed:** Docs/monster_todo.md, codex_log.md
**Outcome:** Added checkmarks and dates for finished tasks.

## [2025-06-08] Fix CLI tests typo
**Prompt:** Replace `subparpers.add_parser` with `subparsers.add_parser` in tests/test_tmcli.py.
**Files Changed:** tests/test_tmcli.py, Docs/CHANGELOG.md, codex_log.md
**Outcome:** Healthcheck subcommand parser now created correctly; pre-commit and pytest pass.
## [2025-06-08] Mark additional completed tasks
**Prompt:** Tick off snapshot alert, self-heal, and delta_tag tasks in monster_todo.md.
**Files Changed:** Docs/monster_todo.md, Docs/CHANGELOG.md, codex_log.md
**Outcome:** Documentation reflects completed features.

## [2025-06-08] Add weekly ROI Telegram command
**Prompt:** Implement /roi command to show current week's profit, ROI, and win/place stats.
**Files Changed:** telegram_bot.py, tests/test_telegram_bot.py, Docs/CHANGELOG.md, Docs/monster_todo.md, README.md, codex_log.md
**Outcome:** Telegram bot now returns weekly ROI summary via /roi.


## [2025-06-08] Add log archiving utility
**Prompt:** Create archive_old_logs.py to zip and move logs older than 14 days into logs/archive/.
**Files Changed:** utils/archive_old_logs.py, tests/test_archive_old_logs.py, Docs/CHANGELOG.md, Docs/monster_todo.md, Docs/monster_overview.md, Docs/script_audit.txt, codex_log.md
**Outcome:** Old log files can be compressed automatically and documentation updated.


## [2025-06-21] Tag Value Wins in ROI tracker
**Prompt:** Update ROI tracker to label winning tips with `odds_delta` > 5.0 as "💸 Value Win".
**Files Changed:** roi/tag_roi_tracker.py, tests/test_model_drift_report.py, Docs/CHANGELOG.md, Docs/monster_todo.md, codex_log.md
**Outcome:** High-delta winners now flagged for future analysis; failing test patched.

## [2025-06-21] Add /nap command to Telegram bot
**Prompt:** Telegram /nap command with stats
**Files Changed:** telegram_bot.py, tests/test_telegram_bot.py, Docs/monster_todo.md, Docs/CHANGELOG.md, Docs/monster_overview.md, codex_log.md
**Outcome:** Bot now reports last NAP results and ROI via /nap command.


## [2025-06-21] Add place-focused training script
**Prompt:** Clone train_model_v6.py to create train_place_model.py predicting top 3 finishes.
**Files Changed:** train_place_model.py, all_scripts.txt, Docs/CHANGELOG.md, Docs/monster_overview.md, Docs/monster_todo.md, README.md, codex_log.md
**Outcome:** New place model training script added and docs updated.

## [2025-06-08] Add bankroll drawdown tracking
**Prompt:** Codex, update roi_tracker_advised.py to include cumulative profit and drawdown tracking in the output logs.
**Files Changed:** roi/roi_tracker_advised.py, roi/weekly_roi_summary.py, Docs/CHANGELOG.md, Docs/monster_overview.md, Docs/monster_todo.md, codex_log.md
**Outcome:** Daily and weekly ROI summaries now display bankroll figures and worst historical drawdown.
## [2025-06-21] Consolidate changelog entries
**Prompt:** Remove ======= lines and merge duplicate 2025-06-08 sections in Docs/CHANGELOG.md.
**Files Changed:** Docs/CHANGELOG.md, codex_log.md
**Outcome:** CHANGELOG.md now has a single well-formatted 2025-06-08 entry.

## [2025-06-23] Remove outdated check_betfair_market_times.py
**Prompt:** Delete or update script per audit. Deleted and cleaned references.
**Files Changed:** utils/check_betfair_market_times.py (deleted), all_scripts.txt, Docs/script_audit.txt, Docs/CHANGELOG.md, Docs/monster_todo.md, codex_log.md
**Outcome:** Unused script removed and documentation updated.



## [2025-06-23] Remove redundant README section
**Prompt:** Delete the duplicate `self_train_from_history.py` paragraph.
**Files Changed:** README.md, Docs/CHANGELOG.md, codex_log.md
**Outcome:** README now contains one complete explanation of the script.
## [2025-06-23] Fix docs links
**Prompt:** Replace `../docs/` with `../Docs/` for script_audit.txt and SECURITY_REVIEW.md.
**Files Changed:** Docs/README.md, README.md, Docs/CHANGELOG.md, codex_log.md
**Outcome:** Documentation links now correctly reference the capitalised Docs directory.



## [2025-06-24] Add tag commentary helper
**Prompt:** Refactor commentary generation into a reusable function and update dispatch logic.
**Files Changed:** utils/commentary.py, core/dispatch_tips.py, Docs/CHANGELOG.md, Docs/monster_overview.md, Docs/monster_todo.md, codex_log.md, tests/test_commentary.py
**Outcome:** Telegram tips and logs now include concise tag-based commentary.

## [2025-06-24] Add Stats API server
**Prompt:** Build stats_api.py that exposes /roi, /tips, /tags endpoints using FastAPI and serve JSON from latest logs.
**Files Changed:** stats_api.py, tests/test_stats_api.py, requirements.txt, Docs/CHANGELOG.md, Docs/monster_todo.md, codex_log.md
**Outcome:** New FastAPI server returns latest ROI, tips and tag summaries for dashboards.


## [2025-06-24] Add Draw Advantage tag
**Prompt:** Enhance inference to tag runners with 📊 Draw Advantage if draw_bias_rank > 0.7.
**Files Changed:** core/run_inference_and_select_top1.py, core/dispatch_tips.py, tests/test_dispatch_tips.py, Docs/CHANGELOG.md, Docs/monster_todo.md, codex_log.md
**Outcome:** Tips JSON now includes the Draw Advantage tag and Telegram commentary reflects the bias.


## [2025-06-24] Add unit test for inference script
**Prompt:** Write unit tests for run_inference_and_select_top1.py.
**Files Changed:** tests/test_run_inference_and_select_top1.py, Docs/CHANGELOG.md, Docs/monster_todo.md, codex_log.md
**Outcome:** Test verifies NAP selection and tagging logic.


## [2025-06-24] Add Telegram confidence commentary
**Prompt:** Enhance `dispatch_tips.py` to add a model confidence line.
**Files Changed:** core/dispatch_tips.py, tests/test_dispatch_tips.py, Docs/CHANGELOG.md, Docs/monster_todo.md, codex_log.md
**Outcome:** Added confidence summary line with tag reasons.

## [2025-06-25] Refactor tips into dataclass
**Prompt:** Refactor tip dictionaries into a Tip dataclass.
**Files Changed:** core/tip.py, core/dispatch_tips.py, core/dispatch_all_tips.py, roi/calibrate_confidence_daily.py, roi/generate_subscriber_log.py, roi/generate_tweet.py, roi/roi_tracker_advised.py, roi/tag_roi_tracker.py
**Outcome:** Scripts now use the dataclass for loading and saving tips.

## [2025-06-23] Add tip_control_panel CLI
**Prompt:** Create tip_control_panel.py script with manual tip selection and Telegram send.
**Files Changed:** tip_control_panel.py, Docs/CHANGELOG.md, Docs/monster_todo.md
**Outcome:** Added interactive CLI for manual dispatch with dev-mode support.
## [2025-06-25] Log Danger Fav outcomes
**Prompt:** Enhance generate_lay_candidates.py to log results of tagged Danger Favs.
**Files Changed:** generate_lay_candidates.py, tests/test_generate_lay_candidates.py, Docs/CHANGELOG.md, Docs/monster_overview.md, Docs/TIPPING_MONSTER_PRODUCTS.md, Docs/monster_todo.md, codex_log.md
**Outcome:** Script now appends daily Danger Fav results to logs/danger_fav_history.csv and optional Telegram summary.

## [2025-06-24] Add /tip Telegram command
**Prompt:** Add new /tip command to Telegram bot returning latest horse tip.
**Files Changed:** telegram_bot.py, tests/test_telegram_bot.py, Docs/CHANGELOG.md, Docs/monster_overview.md, Docs/monster_todo.md, codex_log.md
**Outcome:** Bot replies with confidence, tags, commentary and odds for the requested horse.
## [2025-06-25] Add expressive commentary style
**Prompt:** Add modular tone templates with CLI/env control.
**Files Changed:** utils/commentary.py, tests/test_commentary.py, core/dispatch_tips.py, cli/tmcli.py, Docs/CHANGELOG.md, Docs/monster_todo.md, codex_log.md
**Outcome:** Commentary can be rendered in basic or expressive tone via `--comment-style` or `TM_COMMENT_STYLE`.

## [2025-06-26] Extend rolling ROI tracking
**Prompt:** Implement rolling_roi_30.csv with wins, places, tips and strike rate; auto-update via ROI pipeline.
**Files Changed:** generate_rolling_roi.py, roi/run_roi_pipeline.sh, Docs/CHANGELOG.md, Docs/TIPPING_MONSTER_ROI_OVERVIEW.md, Docs/monster_todo.md, codex_log.md
**Outcome:** New CSV log summarises the last 30 days and is refreshed daily.



## [2025-06-24] Add combo generator
**Prompt:** Create generate_combos.py to suggest doubles and trebles from top tips.
**Files Changed:** generate_combos.py, tests/test_generate_combos.py, Docs/CHANGELOG.md, Docs/monster_overview.md, Docs/quickstart.md, Docs/script_audit.txt, Docs/TIPPING_MONSTER_PRODUCTS.md, Docs/monster_todo.md, codex_log.md
**Outcome:** Added combo generator script and documentation.
