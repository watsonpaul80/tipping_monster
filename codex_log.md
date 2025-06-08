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
=======

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
