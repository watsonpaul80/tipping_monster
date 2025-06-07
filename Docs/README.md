# 🧠 TIPPING MONSTER SYSTEM DOCS

This documentation set covers everything about the **Tipping Monster** project — a fully automated machine learning tip engine for UK/IRE racing.

---

## 📄 Files Included

- `quickstart.md` – brief overview of the repo and where to start.
- `monster_overview.md` – full overview of the main ML pipeline, tip logic, and automation.
- `monster_todo.md` – task tracker for main tipping logic including ROI, model training, and Telegram output.

---

## 🔑 Environment Variables

The scripts expect the following environment variables to be defined:

### 🏇 Betfair API

- `BF_USERNAME`
- `BF_PASSWORD`
- `BF_APP_KEY`
- `BF_CERT_PATH`
- `BF_KEY_PATH`
- `BF_CERT_DIR`

SSL certificates required for Betfair API access should be generated yourself and stored **outside the repository**.

### 📬 Telegram Bot

To send messages via the Telegram bot:

- `TELEGRAM_BOT_TOKEN` *(or `TG_BOT_TOKEN`)*
- `TELEGRAM_CHAT_ID` *(or `TG_USER_ID`)*

Both naming conventions are supported across the codebase for flexibility.

### 📁 Path Config (Optional)

- `TIPPING_MONSTER_HOME` – manually sets the project root.  
  If unset, scripts use:
  ```bash
  git rev-parse --show-toplevel
