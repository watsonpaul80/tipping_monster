# 🧠 TIPPING MONSTER SYSTEM DOCS

This documentation set covers everything about the **Tipping Monster** project — a fully automated machine learning tip engine for UK/IRE racing.

## 📄 Files Included

- `quickstart.md` – brief overview of the repo and where to start.
- `monster_overview.md` – full overview of the main ML pipeline, tip logic, and automation.
- `monster_todo.md` – task tracker for main tipping logic including ROI, model training, and Telegram output.
- `sniper_overview.md` – description of Steam Sniper logic, snapshot timing, detection, and Telegram output.
- `sniper_todo.md` – task tracker for Steam Sniper features, scoring, and automation ideas.


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
- `TIPPING_MONSTER_HOME` (optional) – path to the project root. If unset, scripts use `git rev-parse --show-toplevel`.

Built by Paul. Maintained by Monster. Improved by chaos. 🧠🐎.
