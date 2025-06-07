# 🧠 TIPPING MONSTER SYSTEM DOCS

This documentation set covers everything about the **Tipping Monster** project — a fully automated machine learning tip engine for UK/IRE racing.

## 📄 Files Included

- `quickstart.md` – brief overview of the repo and where to start.
- `monster_overview.md` – full overview of the main ML pipeline, tip logic, and automation.
- `monster_todo.md` – task tracker for main tipping logic including ROI, model training, and Telegram output.
- `sniper_overview.md` – description of Steam Sniper logic, snapshot timing, detection, and Telegram output.
- `sniper_todo.md` – task tracker for Steam Sniper features, scoring, and automation ideas.
- `../docs/script_audit.txt` – summary of active vs. unused scripts with keep/remove/rewrite verdicts.


## 🔑 Environment Variables

The scripts expect the following environment variables to be defined:

- `BF_USERNAME`
- `BF_PASSWORD`
- `BF_APP_KEY`
- `BF_CERT_PATH`
- `BF_KEY_PATH`
- `BF_CERT_DIR`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Built by Paul. Maintained by Monster. Improved by chaos. 🧠🐎.

## `dispatch_all_tips.py`

`dispatch_all_tips.py` formats a day's tips and can post them to Telegram.

- `--telegram` sends the messages via the bot token and chat ID instead of just printing to the console.
- `--batch-size N` controls how many tips are grouped per Telegram message (default 5).
- Make sure `TELEGRAM_CHAT_ID` is set if you enable `--telegram`.

Example:

```bash
python dispatch_all_tips.py --date 2025-06-07 --telegram --batch-size 10
```
