# 📋 STEAM SNIPER — TO-DO LIST (SPRUCED)

A focused to-do list for the Steam Sniper module of Tipping Monster. ✅ = Done, 🔜 = Next Sprint, 🧠 = Future Idea

---

## ✅ COMPLETED

- `build_sniper_schedule.py`: extracts race times and off times
- `generate_and_schedule_snipers.sh`: schedules snapshot runs via `at`
- `run_sniper_pipeline.sh`: end-to-end script for fetching odds, merging, detecting steamers, and dispatching
- `fetch_betfair_sniper_odds.py`: gets odds + volumes
- `merge_sniper_history.py`: merges same-day runner odds
- `detect_and_save_steamers.py`: drops ≥30% vs baseline
- `dispatch_snipers.py`: sends Telegram alerts (max 5 per run)
- `safecron.sh` support added to all sniper jobs
- Snapshot file naming + merge logic all working
- Full cronjob integration at 05:01 (build), 05:02 (load)
- Telegram channel ID usage and output formats confirmed

---

## 🔜 NEXT SPRINT

- [ ] Add steamer confidence score from ML model
- [ ] Score steamers based on trend shape (progressive drops)
- [ ] Include trainer/jockey form overlay
- [ ] Create batch cronjob for testing dispatch without triggering Telegram
- [ ] Create `sniper_tag` field (used in main tip system if sniped later)
- [ ] Store all steamer history to `steam_sniper_intel/history/`

---

## 🧠 FUTURE IDEAS

- Suppress low-confidence steamers based on odds floor (e.g. >25/1)
- Combine Sniper with final NAP filter 15 mins before race
- Build a scoring model (Steam Intensity Index) combining drop %, volume, speed
- Add chart-based Telegram output (sparkline odds trend)
- Trigger Monster commentary on top 3 steamers of the day

---

## ⏰ CRON + TIMING RECAP

- `build_sniper_schedule.py`: 05:01 AM
- `generate_and_schedule_snipers.sh`: 05:02 AM
- Jobs fire via `at` for each race at:
  - T-60, T-30, T-10 mins

Example:
- For 14:20 race → snapshot times are 13:20, 13:50, 14:10

---

Let me know when you're ready to merge this into a ZIP or generate the `monster_todo.md`.

🔥 Steam Sniper Backlog
 Auto-trigger evaluate_steamers.py after each snapshot is compared

 Enhance Telegram messages to include:

Odds at 08:00

Current odds

Drop %

Race time and horse

 Delay logic: If a horse steams at T-60, log it. If it steams more at T-30 or T-10, show progression

 Track how many steamers win/place per day/week (ROI of steamers)

 Auto-broadcast: "🔥 Steam Sniper Activated" banner when first steamer found that day

 Add LLM summary per steamer: “Why this may be steam” (optional)

 🧠 Steam Sniper Intelligence Upgrade – Task List
🔥 Phase 1: Market Insight Overlay
[ ] Odds Progression Tracking

Track each horse's odds at 08:00, T-60, T-30, T-10

Store progression in JSON

Add progression line to Telegram message:

"Was 20/1 → 14/1 → 10/1 → now 7/1"

[ ] Volume-Aware Steam Detection

Query Betfair for total matched volume per horse

Add a minimum threshold (e.g. >£1,000 matched)

Prioritize high-liquidity steamers

[ ] Telegram Output: Steam Confidence Tier

Tag each steamer as:

🟢 High Confidence (form + volume + drop)

🟡 Moderate (price only)

🔴 Low Confidence (suspicious or weak)

🔍 Phase 2: Contextual Awareness
[ ] Trainer & Jockey Form Overlay

Use daily in-form data (already generated)

Add inline form badge to steamer message:

“Trainer: 🔥 3 wins last 5 days”

[ ] Add Course/Distance/Going Profile Check

Cross-reference rpscrape form fields

Highlight if horse is CD winner, or proven on today’s going

🤖 Phase 3: ML-Powered Sniper Scoring
[ ] Build Steamer Profile Dataset

Log past steamers with:

Odds movement

Result

Volume

Form tags

Race type

Store in logs/steamers_profile.csv

[ ] Train Binary Classifier (Win / No Win)

XGBoost or similar

Learn which types of steamers are likely to win

[ ] Add Model Scoring to Live Alerts

Predict win probability

Only dispatch steamers above X threshold (e.g. >25% win chance)

🧠 Phase 4: Monster ROI Intelligence
[ ] Sniper ROI By Confidence Tier

Track win %, place %, ROI for:

🟢 High

🟡 Moderate

🔴 Low

Add to weekly summary

[ ] Optional: Simulate staking strategy

Higher stakes on 🟢 vs small token on 🔴

API key ZcK5mXdXVDcvZwPgwc3Oywu2K API key secret esLc5AVS963wPcdBfOFKUYSpbCJVosNQk8nbuxIEco3pKTi4LB bearer token AAAAAAAAAAAAAAAAAAAAAAqUsQEAAAAAvrUasA%2BVZ9VqVm2%2BAbHFCl962cY%3DzhxWISpcFN03GCATZiSCm1QRIdbiTSpXh8rgjS2I5JpTHmCTUx access token 22272141-T6aJ4ceahwnc3C1Dm7uMj1whLi9VMWTq7Dx6FUe0A access token secret EW70sC3cnLqOXOyHzUR7NaC2HCDFJfmgVMVdoEcl1rtW9 2 yes, its going to my personal account for now as i have a half decent following  3 looks spot on 