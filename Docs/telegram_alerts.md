# Telegram Alerts & Environment Variables

This page summarises the Telegram-related environment variables and where they are used within the Tipping Monster codebase.

## Environment Variables

- `TELEGRAM_BOT_TOKEN` – primary bot token for sending messages.
- `TG_BOT_TOKEN` – alternate token name used by cron helpers and the morning digest.
- `TELEGRAM_CHAT_ID` – chat or user ID receiving messages.
- `TG_USER_ID` – alternate chat ID variable for `safecron.sh` and `morning_digest.py`.
- `TELEGRAM_DEV_CHAT_ID` – chat ID used when `TM_DEV=1`.
- `PAUL_TELEGRAM_ID` – Paul's user ID for admin-only commands in `telegram_bot.py`.
- `TM_DEV` – if set, redirects messages to `TELEGRAM_DEV_CHAT_ID`.
- `TM_DEV_MODE` – disables all Telegram posts and logs messages locally.

## Usage by Script

| Script | Variables | Purpose |
|-------|-----------|---------|
| `core/dispatch_tips.py` | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | Sends the daily Monster tips. |
| `core/dispatch_all_tips.py` | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | Posts a full racecard of tips. |
| `dispatch_danger_favs.py` | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | Alerts about short‑priced favourites to lay. |
| `generate_combos.py` | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | Sends doubles and trebles. |
| `roi/send_daily_roi_summary.py` | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | Daily ROI summary. |
| `roi/weekly_roi_summary.py` | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | Weekly ROI + chart. |
| `track_lay_candidates_roi.py` | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | Summarises lay candidate results. |
| `scripts/morning_digest.py` | `TG_BOT_TOKEN`, `TG_USER_ID` | Daily checklist of pipeline status. |
| `core/run_pipeline_with_venv.sh` | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | Warns if no tips were dispatched. |
| `telegram_bot.py` | `TELEGRAM_BOT_TOKEN`, `PAUL_TELEGRAM_ID`, `TM_DEV_MODE` | Interactive bot commands. |
| `utils/safecron.sh` | `TG_BOT_TOKEN`, `TG_USER_ID`, `TM_DEV_MODE` | Sends cron failure alerts. |

Most other scripts call `tippingmonster.send_telegram_message`, which respects `TM_DEV` and `TM_DEV_MODE` to route or suppress notifications.

`utils/safecron.sh` wraps cron jobs and posts an alert with `TG_BOT_TOKEN`/`TG_USER_ID` if a job exits non‑zero, unless `TM_DEV_MODE=1` is active.
# Telegram Alerts

This guide summarises all environment variables related to Telegram notifications and which scripts use them.

## Environment variables

- `TELEGRAM_BOT_TOKEN` / `TG_BOT_TOKEN` – bot token used for all Telegram messages.
- `TELEGRAM_CHAT_ID` / `TG_USER_ID` – default chat ID to receive messages.
- `TELEGRAM_DEV_CHAT_ID` – alternate chat ID when `TM_DEV=1`.
- `PAUL_TELEGRAM_ID` – authorisation ID for privileged bot commands.
- `TM_DEV` – routes Telegram posts to `TELEGRAM_DEV_CHAT_ID`.
- `TM_DEV_MODE` – when set to `1`, suppresses Telegram posts and logs them to `logs/dev/` instead.

## Scripts and messages

- **tippingmonster/utils.py** implements `send_telegram_message` and `send_telegram_photo`. These helpers load the bot token and chat ID, honour `TM_DEV` and `TM_DEV_MODE` and are called by most scripts.
- **core/dispatch_tips.py** and **core/dispatch_all_tips.py** send the day's tips.
- **dispatch_danger_favs.py** posts daily danger-favourite alerts.
- **generate_combos.py**, **generate_lay_candidates.py**, **track_lay_candidates_roi.py** and **roi/*.py** scripts send ROI summaries and combo updates.
- **model_feature_importance.py** and **tip_control_panel.py** post images or interactive messages.
- **telegram_bot.py** runs the interactive bot using `TELEGRAM_BOT_TOKEN` and restricts `/override_conf` and other admin commands to `PAUL_TELEGRAM_ID`.
- **utils/safecron.sh** posts cron failure alerts with `TG_BOT_TOKEN` and `TG_USER_ID` when a job exits non‑zero.

## Cron failure alerts

`safecron.sh` captures the last lines of the job log and sends an alert if the exit code is non‑zero. Alerts are skipped when `TM_DEV_MODE=1`.
Before running `safecron.sh`, ensure both `TG_BOT_TOKEN` and `TG_USER_ID` are set in your environment so failure alerts can be sent.
