#!/bin/bash
# safecron.sh <jobname> <command> [args...]

JOB_NAME="$1"
shift
CMD="$@"

LOG_DIR="/home/ec2-user/tipping-monster/logs"
LOG_FILE="${LOG_DIR}/${JOB_NAME}_$(date +%F).log"

mkdir -p "$LOG_DIR"

# Function to send telegram alert on failure
send_telegram_alert() {
  LOG_TAIL=$(tail -n 10 "$LOG_FILE" | sed 's/`/\\`/g' | sed ':a;N;$!ba;s/\n/\\n/g')
  curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d chat_id="${TELEGRAM_CHAT_ID}" \
    -d parse_mode=Markdown \
    -d text=$'⚠️ *Cron Failure Detected*\n*Job:* \`'"$JOB_NAME"$'\`\n*Exit Code:* '"$STATUS"$'\n*Time:* '"$(date)"$'\n*Log:*\n```\n'"$LOG_TAIL"$'\n```'
}

# Run the provided command and capture the exit status
eval "$CMD" >> "$LOG_FILE" 2>&1
STATUS=$?

# If error, send Telegram alert
if [ $STATUS -ne 0 ]; then
  send_telegram_alert
fi

exit $STATUS

