#!/bin/bash
# safecron.sh <jobname> <command> [args...]

JOB_NAME="$1"
shift
CMD="$@"

LOG_DIR="/home/ec2-user/tipping-monster/logs"
LOG_FILE="${LOG_DIR}/${JOB_NAME}_$(date +%F).log"

mkdir -p "$LOG_DIR"

# Run the command and log output
eval "$CMD" >> "$LOG_FILE" 2>&1
STATUS=$?

if [ $STATUS -ne 0 ]; then
  LOG_TAIL=$(tail -n 10 "$LOG_FILE" | sed 's/`/\\`/g' | sed ':a;N;$!ba;s/\n/\\n/g')

  curl -s -X POST https://api.telegram.org/bot6298132668:AAGja-iEQzAK1Ri5jBOoHwP4-YWZuywKjNU/sendMessage \
    -d chat_id=1054773464 \
    -d parse_mode=Markdown \
    -d text=$'⚠️ *Cron Failure Detected*\n*Job:* \`'"$JOB_NAME"$'\`\n*Exit Code:* '"$STATUS"$'\n*Time:* '"$(date)"$'\n*Log:*\n```\n'"$LOG_TAIL"$'\n```'
fi

