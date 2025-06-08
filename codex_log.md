## [2025-06-08] Remove invalid model_drift_report install
**Prompt:** Fix GitHub workflow failing because package `model_drift_report` is missing.
**Files Changed:** .github/workflows/python-tests.yml, Docs/CHANGELOG.md, codex_log.md
**Outcome:** Workflow now installs only standard dependencies and uses local module.
