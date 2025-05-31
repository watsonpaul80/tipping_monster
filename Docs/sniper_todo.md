## 🔫 Steam Sniper – May 31 Fixes & Backlog

### ✅ Completed Fixes (May 31)
- Fixed issue where sniper jobs weren’t triggering due to empty schedule.
- Identified root cause: `build_sniper_schedule.py` ran too early (09:15) before racecards were fully available.
- Cron adjusted to:
  - `30 9 * * *` → `build_sniper_schedule.py`
  - `35 9 * * *` → `generate_and_schedule_snipers.sh`
- Confirmed racecard scraping completes by then in most cases.
- Race time parser patched to support both 12-hour (`3:15`) and 24-hour (`15:15`) formats.
- Manually validated that sniper jobs now schedule and dispatch correctly (e.g. 14:45, 15:05).
- Confirmed `wait_for_racefile()` already ensures the file exists before running.

---

### 🔜 Backlog – Sniper Improvements

#### 🛠️ Robustness & Monitoring
- [ ] Retry logic if no valid race times found after file exists (e.g. retry every 10s for 2 mins).
- [ ] Send Telegram alert if schedule is empty after building.
- [ ] Save daily schedule log to `logs/sniper_schedule_YYYY-MM-DD.log` for audit/debug.

#### 📈 ROI + Outcome Feedback
- [ ] Track win %, place %, and ROI of steamers per snapshot/day/week.
- [ ] Log results to `logs/sniper_results_YYYY-MM-DD.csv` or similar.
- [ ] Integrate sniper ROI into `weekly_roi_summary.py` for Telegram reporting.

#### 💬 Telegram Message Polish
- [ ] Show odds progression in alert (e.g. `20/1 → 12/1 → 7/1`).
- [ ] Include drop %, matched volume, and market trend.
- [ ] Add "Steam Confidence Tier" label:
  - 🟢 High (volume + form + big drop)
  - 🟡 Moderate (price only)
  - 🔴 Low (low volume, weak context)
- [ ] Optional: Add LLM commentary to explain the steamer pick.

#### 🤖 ML-Powered Steam Detection (Phase 2)
- [ ] Log historical steamers to `steamers_profile.csv` with result, odds movement, volume, tags.
- [ ] Train classifier to predict win chance based on steamer profile.
- [ ] Only dispatch steamers with predicted win chance > X% (e.g. 25%+)
- [ ] Add predicted win chance to Telegram alerts for elite filtering.

---
