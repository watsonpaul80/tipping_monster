#!/bin/bash
script="steam_sniper_schedule.sh"
line_buffer=""

while IFS= read -r line; do
  # Skip shebang or empty lines
  [[ "$line" =~ ^#! ]] && continue
  [[ -z "$line" ]] && continue

  line_buffer+="$line"$'\n'

  # Schedule when we have a full 3-line block
  if [[ $(echo "$line_buffer" | grep -c 'fetch_betfair_odds.py') -eq 1 ]] && \
     [[ $(echo "$line_buffer" | grep -c 'compare_odds_to_0800.py') -eq 1 ]]; then

    label=$(echo "$line_buffer" | grep fetch_betfair_odds | grep -oP 'label \K[0-9]+')
    if [[ "$label" =~ ^[0-9]{4}$ ]]; then
      hour="${label:0:2}"
      minute="${label:2:2}"
      echo "$line_buffer" | at "$hour:$minute" 2>/dev/null
      echo "⏱ Scheduled: $hour:$minute"
    else
      echo "[⛔️] Invalid label, skipping block:"
      echo "$line_buffer"
    fi
    line_buffer=""
  fi
done < "$script"

echo "✅ All sniper jobs loaded into 'at' scheduler."

