# 🧠 TIPPING MONSTER SYSTEM DOCS

This documentation set covers everything about the **Tipping Monster** project — a fully automated machine learning tip engine for UK/IRE racing.

---

## 📄 Files Included

- `quickstart.md` – brief overview of the repo and where to start.
- `monster_overview.md` – full overview of the main ML pipeline, tip logic, and automation.
- `monster_todo.md` – task tracker for main tipping logic including ROI, model training, and Telegram output.
- `monster_todo_v2.md` – high-level roadmap for upcoming features.
- `dev_command_reference.md` – quick list of useful developer commands.
- `prod_setup_cheatsheet.md` – dev-to-prod reference.
 - `../Docs/script_audit.txt` – summary of active vs. unused scripts with keep/remove/rewrite verdicts.
 - `../Docs/SECURITY_REVIEW.md` – latest security audit notes.

---

## 🔑 Environment Variables

Create a `.env` file (see `.env.example`) with the following variables:

- `BF_USERNAME`
- `BF_PASSWORD`
- `BF_APP_KEY`
- `BF_CERT_PATH`
- `BF_KEY_PATH`
- `BF_CERT_DIR`
- `TELEGRAM_BOT_TOKEN`
- `TG_BOT_TOKEN` (optional alias for `TELEGRAM_BOT_TOKEN`)
- `TELEGRAM_CHAT_ID`
- `TG_USER_ID` (optional alias for `TELEGRAM_CHAT_ID`)
- `TELEGRAM_DEV_CHAT_ID` (used when `TM_DEV=1`; ignored when `TM_DEV_MODE=1`)
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION`
- `TM_DEV` (routes Telegram messages to `TELEGRAM_DEV_CHAT_ID`)
- `TM_DEV_MODE` (disables Telegram/Twitter posts and logs locally)

Set `TM_DEV=1` to route Telegram messages to `TELEGRAM_DEV_CHAT_ID`.
Set `TM_DEV_MODE=1` to suppress all Telegram sends and write to `logs/dev/` instead.
Running scripts with the `--dev` flag automatically sets `TM_DEV_MODE=1`.
The `utils/safecron.sh` helper also respects this variable and will not send
Telegram alerts when `TM_DEV_MODE=1`.
See `telegram_alerts.md` for a full list of Telegram variables and the scripts that use them.

For a detailed breakdown of each Telegram variable and how they are used, see
[`telegram_alerts.md`](telegram_alerts.md).

You can copy `.env.example` to `.env` and fill in your credentials for local development.

---

## `dispatch_all_tips.py`

`dispatch_all_tips.py` formats a day's tips and can post them to Telegram.

- `--telegram` sends the messages via the bot token and chat ID instead of just printing to the console.
- `--batch-size N` controls how many tips are grouped per Telegram message (default 5).
- Make sure `TELEGRAM_CHAT_ID` is set if you enable `--telegram`.

Example:

```bash
python dispatch_all_tips.py --date 2025-06-07 --telegram --batch-size 10

Built by Paul. Maintained by Monster. Improved by chaos. 🧠🐎.

### Running Inference

Run inference scripts from the repository root. Example:

```bash
python core/run_inference_and_select_top1.py
```
Running this command inside `core/` will fail with `ModuleNotFoundError` unless `PYTHONPATH=..` is configured.

