# TIPPING MONSTER MASTER BLUEPRINT (v6+) - TO-DO LIST

This document outlines all current in-progress tasks, backlog items, strategic future enhancements, and new ideas for the Tipping Monster system.

---

### 🔜 In Progress / Backlog (v6 Polish)

These are tasks that are either **partially complete** or **next in line for development** within the current v6 framework.

* [ ] [#001] Suppression logic based on band ROI performance  
* [ ] [#002] Highlight best/worst bands visually in summary  
* [ ] [#003] Weekly retraining instead of daily (optional)  
* [ ] [#004] Auto-send subscriber-friendly ROI summary to Telegram channel  

---

### 🧠 Backlog: v7 Features & Enhancements

#### ⚙️ Confidence Filtering

* [ ] [#005] Passive tracking of 0.50–0.80 band ROI (no suppression)  
* [ ] [#006] Activate suppression logic based on band ROI performance  

#### 📊 Model Explainability

* [ ] [#007] SHAP or feature gain per model  
* [ ] [#008] Top 5 feature impact per tip (in .md + Telegram)  

#### 🗣 Commentary Enhancements

* [ ] [#009] Add logic-based commentary block: “📉 Class Drop, 📈 In Form, Conf: 92%”  
* [ ] [#010] Use tags + confidence + form stats for explanation  

#### 💰 Monetisation Logic

* [ ] [#011] Score tips by band, confidence, and value  
* [ ] [#012] Tag top 3 per day as Premium Tips  
* [ ] [#013] Split public vs subscriber tips via logic or tier  

#### 📈 Tag ROI Tracking

* [ ] [#014] ROI breakdown by confidence band, tip type, and tag  
* [ ] [#015] Show top ROI tags daily  

#### 🧪 Experimental

* [ ] [#016] Telegram control panel for config (bands, filters)  
* [ ] [#017] Parallel model comparison (v6 vs v7)  
* [ ] [#018] Drawdown tracking in ROI logs  

---

### 🔭 Strategic Enhancements

#### ML & Confidence Improvements

* [ ] [#019] Place-focused model (predict 1st–3rd)  
* [ ] [#020] Confidence regression model (predict prob, not binary)  
* [ ] [#021] ROI-based calibration (not just accuracy)  
* [ ] [#022] Penalise stale horses and poor form  

#### ROI Visualisation

* [ ] [#023] Add weekly ROI line chart (matplotlib) to logs  
* [ ] [#024] Include win/loss emoji outcomes in Telegram ROI  
* [ ] [#025] Optional: highlight top winners in Telegram  

#### Public Polish & Delivery

* [ ] [#026] NAP-only output mode for casual tier  
* [ ] [#027] Invite-only Telegram access logic  
* [ ] [#028] Visual dashboards (Streamlit / HTML)  
* [ ] [#029] Monetisation hooks (Stripe, Patreon, etc.)  

---

### 🔁 Realistic Odds Integration

**Goal:** Improve ROI transparency by replacing inaccurate SPs with realistic odds from pre-race snapshots.

* [x] [#030] Build `extract_best_realistic_odds.py` to inject best odds before race  
* [x] [#031] Output `logs/sent_tips_YYYY-MM-DD_realistic.jsonl`  
* [x] [#032] Update ROI tracker to prefer realistic odds over `bf_sp`  
* [x] [#033] Show “Realistic Odds Mode” label in ROI summary  
* [ ] [#034] Log delta: `realistic_odds - bf_sp` in ROI logs  
* [ ] [#035] Optional: Show delta highlights in Telegram ROI (e.g. “💸 14/1 ➝ 4.3”)  
* [ ] [#036] Track performance of tips with high odds delta (market steamers)  
* [ ] [#037] Add `odds_delta` to ML training later as input signal  

---

### 💡 Ideas & Pipeline Quality

* [ ] [#038] Fallback logic if `logs/sent_tips.jsonl` is missing  
* [ ] [#039] Alert if dispatch runs but no tips are sent  
* [ ] [#040] Alert if odds snapshot fails or returns too few runners  
* [ ] [#041] Self-heal for missing `logs/`, retry on failure  

---

### 🧠 Learning from Odds Delta

**Goal:** Train Monster to learn from large market moves.

* [ ] [#042] Calculate and store `odds_delta` (realistic - SP)  
* [ ] [#043] Score tips based on delta + result + confidence  
* [ ] [#044] Reward positive delta wins, penalise drifts  
* [ ] [#045] Add `delta_tag` to messages (e.g. “🔥 Market Mover”)  
* [ ] [#046] Use as feature or reinforcement signal in future models  

---

### 📈 Business & Monetisation Tasks

#### Phase 1: Free Launch

* [x] [#047] Weekly + daily ROI tracking in Telegram  
* [x] [#048] ROI logic documented  
* [ ] [#049] Build basic landing page  
* [ ] [#050] Setup `/join` or invite-link system  

#### Phase 2: Trust Builder

* [ ] [#051] Public ROI dashboard (Google Sheets / CSV)  
* [ ] [#052] Share summaries on Reddit/forums weekly  
* [ ] [#053] Capture emails or poll interest  
* [ ] [#054] Trial affiliate links with tracking  

#### Phase 3: Monetisation

* [ ] [#055] Stripe/Patreon integration  
* [ ] [#056] “Monster Premium” Telegram channel  
* [ ] [#057] Post pinned weekly ROI + tip snapshot  
* [ ] [#058] Sell tip packs, stats, NAPs, etc.  

#### Bonus

* [ ] [#059] Add /roi, /stats, /nap bot commands  
* [ ] [#060] Add Telegram confidence commentary  
* [ ] [#061] Optional intro video of how Monster works  
