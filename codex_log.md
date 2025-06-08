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

