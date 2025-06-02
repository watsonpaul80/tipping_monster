# 🔫 STEAM SNIPER TODO — As of 2025-06-01

## ✅ Completed Tasks

1. ✅ Parse real race times from `rpscrape/batch_inputs/YYYY-MM-DD.jsonl`
2. ✅ Extract HH:MM from `"race": "HH:MM Venue"` fields
3. ✅ Build snapshot schedule for each race at T-60, T-30, T-10 mins
4. ✅ Skip snapshot times already in the past (real-time check)
5. ✅ Save to `steam_sniper_intel/sniper_schedule.txt` in 24h format
6. ✅ Create `run_sniper_pipeline.sh` to:
    - Read schedule
    - Schedule `at` jobs for each time
    - Each job runs snapshot + steamer dispatch
7. ✅ Ensure 08:00 snapshot captured for baseline comparison
8. ✅ Validate all paths in `build_sniper_schedule.py` (abs not rel)
9. ✅ Fix f-string issues in Python 3 print lines (e.g. emojis)
10. ✅ Cap Telegram dispatches at 20 steamers per message
11. ✅ Print job numbers and timestamps when scheduling (`atq` visible)
12. ✅ Manual override working to re-run snapshots/dispatches
13. ✅ System fully functional from racecard to sniper alerts (v1 live)

---

## 🧪 In Progress

14. 🔄 Monitor `at` queue to confirm jobs run on time
15. 🧪 Verify `odds_snapshots/` and `steamers_*.json` are saved correctly
16. 🧪 Validate Telegram formatting is consistent, readable, and spaced
17. 🔁 Test behavior if 08:00 snapshot is missing (fallback logic)

---

## 🔜 Next Up

18. 📊 Score steamers based on:
    - % drop from 08:00
    - Monster tip? (yes/no)
    - Trainer/Jockey form (if available)
19. 🚦 Add steamer confidence tags (e.g. High / Medium / Low)
20. 🧠 Emoji overlays:
    - 🔥 Big market mover
    - 🧨 Drop > 50%
    - 🐎 Previously tipped
21. 💾 Save each Telegram dispatch to local `logs/sniper_telegram_*.txt`
22. 🗂️ Inject steamers into `sent_tips_*_snipers.jsonl` for ROI tracking

---

## 🧠 Future Enhancements (Backlog)

23. 🧮 Overlay trainer/jockey 14-day form in steamer messages
24. 📈 Track steamer win/place ROI over time (daily + weekly)
25. 📬 Add Discord and email alert support
26. 🧵 Group steamers by race with “👀 Watch this race” tags
27. 🧪 Flag steamers that drifted back (reverse steam detection)
28. 💡 Add ML-based filtering to reduce false positives
29. 📉 Monitor odds *velocity* (rate of change, not just % drop)
30. 🛠️ Create `sniper_test_runner.py` to simulate pipeline offline
31. 🧠 Auto-label potential *value bets* (if odds > implied chance)

---

## 🚀 Milestone

🎯 **v1.0 (Live Sniper Launch) Achieved**  
All core components live and functioning:
- ✅ Snapshot collection
- ✅ Steam detection
- ✅ Telegram dispatch
- ✅ Schedule runner via `at`
- ✅ Fully race-aware dynamic pipeline

