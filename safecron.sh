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
  curl -s -X POST https://api.telegram.org/bot6298132668:AAGja-iEQzAK1Ri5jBOoHwP4-YWZuywKjNU/sendMessage \
    -d chat_id=1054773464 \
    -d parse_mode=Markdown \
    -d text=$'⚠️ *Cron Failure Detected*\n*Job:* \`'"$JOB_NAME"$'\`\n*Exit Code:* '"$STATUS"$'\n*Time:* '"$(date)"$'\n*Log:*\n```\n'"$LOG_TAIL"$'\n```'
}

# Check if job matches sniper tasks and run accordingly
case "$JOB_NAME" in
  build_sniper_intel)
    source /home/ec2-user/tipping-monster/.venv/bin/activate
    /home/ec2-user/tipping-monster/.venv/bin/python /home/ec2-user/tipping-monster/steam_sniper_intel/build_sniper_schedule.py "$@" >> "$LOG_FILE" 2>&1
    STATUS=$?
    ;;
  load_sniper_intel)
    source /home/ec2-user/tipping-monster/.venv/bin/activate
    /bin/bash /home/ec2-user/tipping-monster/steam_sniper_intel/generate_and_schedule_snipers.sh "$@" >> "$LOG_FILE" 2>&1
    STATUS=$?
    ;;
  *)
    # Default: run the passed command as is
    eval "$CMD" >> "$LOG_FILE" 2>&1
    STATUS=$?
    ;;
esac

# If error, send Telegram alert
if [ $STATUS -ne 0 ]; then
  send_telegram_alert
fi

exit $STATUS

