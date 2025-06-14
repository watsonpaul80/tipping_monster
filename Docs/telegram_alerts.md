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

