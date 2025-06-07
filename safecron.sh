#!/bin/bash
# safecron.sh <jobname> <command> [args...]

JOB_NAME="$1"
shift
CMD="$@"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${TIPPING_MONSTER_HOME:-$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)}"

LOG_DIR="$REPO_ROOT/logs"
LOG_FILE="${LOG_DIR}/${JOB_NAME}_$(date +%F).log"

if [[ -z "$TG_BOT_TOKEN" || -z "$TG_USER_ID" ]]; then
  echo "Error: TG_BOT_TOKEN and TG_USER_ID must be set" >&2
  exit 1
fi

mkdir -p "$LOG_DIR"

# Function to send telegram alert on failure
send_telegram_alert() {
  LOG_TAIL=$(tail -n 10 "$LOG_FILE" | sed 's/`/\\`/g' | sed ':a;N;$!ba;s/\n/\\n/g')
  curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d chat_id="${TELEGRAM_CHAT_ID}" \
    -d parse_mode=Markdown \
    -d text=$'⚠️ *Cron Failure Detected*\n*Job:* \`'"$JOB_NAME"$'\`\n*Exit Code:* '"$STATUS"$'\n*Time:* '"$(date)"$'\n*Log:*\n```\n'"$LOG_TAIL"$'\n```'
}


# Run the provided command and capture its exit status
eval "$CMD" >> "$LOG_FILE" 2>&1
STATUS=$?

# If error, send Telegram alert
if [ $STATUS -ne 0 ]; then
  send_telegram_alert
fi

exit $STATUS

