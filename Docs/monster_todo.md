# 🧠 TIPPING MONSTER — PRIORITISED MASTER TODO

A living roadmap of every feature, fix, and dream for the Tipping Monster system.  
**Numbered by priority.**  
**✅ = Complete** | **🔥 = High Priority** | **🧪 = Experimental** | **💡 = Idea** | **📈 = Business** | **🔁 = Odds** | **🧠 = ML/Model**

---

## 🔥 HIGH PRIORITY (Current Sprint)

1. ✅ **ML-Based Commentary System** — tag-based smart summaries (no LLM)  
   ✍️ Already implemented: logic-driven blurbs like  
   “✍️ yard in form, fresh off a short break.”  
   ✅ Confirmed working with tags such as Fresh, Light Weight, Class Drop, etc.  
   🗂️ Each summary also saved per tip in logs (consider foldered logs per tip if expanding)

2. ✅ **`.env` Secrets Refactor** — move Telegram token, AWS keys, etc. out of scripts *(2025-06-08)*

3. ✅ **Model v6 vs v7 Shadow Compare** — dual pipeline + logging for ROI comparison

4. ✅ **Dev Env Completion** — `Makefile`, `dev-check.sh`, log consistency *(2025-06-08)*

5. ✅ **Sort `logs/` Folder** — subfolders for `roi/`, `dispatch/`, `inference/`

6. ✅ **Script Audit** — identify redundant scripts and prune/rename as needed *(2025-06-08)*

7. ✅ **`--dev` Flag Support Across Scripts** — override to prevent real S3 upload, redirect Telegram to personal channel, log to dev folder [Done: 2025-06-29]

8. ✅ **NAP Sanity Filter + Override** — block NAPs over odds cap (e.g. 20/1), allow fallback tag, optional manual override field

---

## 🛠️ MEDIUM PRIORITY (Next Sprint)

9. ✅ Suppression logic based on band ROI performance *(2025-06-08)*
10. ✅ Highlight best/worst bands visually in summary *(Done: 2025-06-25)*
11. ✅ Weekly retraining instead of daily (optional) *(2025-06-08)*
12. Telegram `/rate` Feature — rate personal picks with ML feedback  
13. ✅ Telegram Tip Control Panel — send custom messages, full racecards, etc. [Done: 2025-06-23]
14. 🟡 *Removed for now* – breeding logic too hard to track without structured data  
15. Trainer/Jockey ROI Leaderboard — daily form summary or on-demand stats  
16. All Tips Mode — dispatch full racecards (mug mode) alongside Monster Tips  
17. ✅ SHAP or feature gain per model *(Live internally - 2025-06-08)*
18. ~~Top 5 feature impact per tip (in .md + Telegram)~~ ✅ Implemented via `explain_model_decision.py` and `dispatch_tips.py --explain`
19. ✅ Logic-based commentary block: “📉 Class Drop, 📈 In Form, Conf: 92%” [Done: 2025-06-24]
20. Use tags + confidence + form stats for explanation  
21. ✅ Score tips by band, confidence, and value *(Done: 2025-06-24)*
22. Tag top 3 per day as Premium Tips  
23. Split public vs subscriber tips via logic or tier  
24. ROI breakdown by confidence band, tip type, and tag  
25. ✅ Show top ROI tags daily *(Done: 2025-06-22)*
26. Telegram control panel for config (bands, filters)  
27. ✅ Parallel model comparison (v6 vs v7) *(2025-06-08)*
28. ✅ Drawdown tracking in ROI logs *(Done: 2025-06-08)*

---

## 🔭 STRATEGIC ENHANCEMENTS (v8+ & BEYOND)

29. ✅ Place-focused model (predict 1st–3rd) *(Done: 2025-06-21)*
30. Confidence regression model (predict prob, not binary)  
31. ✅ ROI-based calibration (not just accuracy) *(2025-06-08)*
32. ✅ Penalise stale horses and poor form *(Done: 2025-06-25)*
33. ✅ Add weekly ROI line chart (matplotlib) to logs *(Done: 2025-06-26)*
34. Include win/loss emoji outcomes in Telegram ROI  
35. Optional: highlight top winners in Telegram  
36. NAP-only output mode for casual tier  
37. Invite-only Telegram access logic  
38. Visual dashboards (Streamlit / HTML)  
39. Monetisation hooks (Stripe, Patreon, etc.)

---

## 🔁 REALISTIC ODDS INTEGRATION

40. ✅ Inject best odds with `extract_best_realistic_odds.py`  
41. ✅ Output `logs/dispatch/sent_tips_YYYY-MM-DD_realistic.jsonl`
42. ✅ ROI tracker prefers `realistic_odds` over `bf_sp`  
43. ✅ “Realistic Odds Mode” label in ROI summary  
44. ✅ Log delta: `realistic_odds - bf_sp` in ROI logs  
45. Optional: Telegram ROI summary includes delta emoji (e.g. “💸 14/1 ➝ 4.3”)  
46. ✅ Track high-delta tips separately [Done: 2025-06-21]
47. Add `odds_delta` to ML training as signal

---

## 💡 IDEAS & PIPELINE QUALITY

48. ✅ Fallback logic if `logs/sent_tips.jsonl` is missing
49. ✅ Alert if dispatch runs but no tips are sent
50. ✅ Alert if odds snapshot fails or returns too few runners [Done: 2025-06-08]
51. ✅ Self-heal for missing logs, retry on failure [Done: 2025-06-08]

### 🧼 Log Management Enhancements (User Suggested)

* [x] [#062] Auto-archive old logs into `.zip` files (e.g. logs older than 14 days) [Done: 2025-06-08]
* [x] [#063] Add `logs/healthcheck.log` to flag missing files (e.g., snapshot, results, tips)
* [x] [#064] Stream `logs/roi/` and `logs/dispatch/` (formerly `logs/roi_logs/` and `logs/dispatch_logs/`) to S3 daily for backup
* [x] [#065] Add daily check script to verify all expected logs were created and non-empty

---

## 🧠 LEARNING FROM ODDS DELTA

52. ✅ Calculate and store `odds_delta` (realistic - SP)  
53. Score tips based on delta + result + confidence  
54. Reward positive delta wins, penalise drifts  
55. ✅ Add `delta_tag` to messages (e.g. “🔥 Market Mover”) [Done: 2025-06-08]
56. Use as feature or reinforcement signal in future models

---

## 📈 BUSINESS & MONETISATION

### Phase 1: Free Launch
57. ✅ Weekly + daily ROI tracking in Telegram  
58. ✅ ROI logic documented  
59. Build basic landing page  
60. Setup `/join` or invite-link system

### Phase 2: Trust Builder
61. Public ROI dashboard (Google Sheets / CSV)  
62. Share summaries on Reddit/forums weekly  
63. Capture emails or poll interest  
64. Trial affiliate links with tracking

### Phase 3: Monetisation
65. Stripe/Patreon integration  
66. “Monster Premium” Telegram channel  
67. Post pinned weekly ROI + tip snapshot  
68. Sell tip packs, stats, NAPs, etc.

### Bonus Features / Engagement
69. ✅ Add /roi, /stats, /nap bot commands [Done: 2025-06-21]
70. ✅ Add Telegram confidence commentary [Done: 2025-06-24]
71. Optional intro video of how Monster works

---

## ✅ ROI SYSTEM TODO (NEW FEATURES)

72. ✅ Paul's View Dashboard – private ROI explorer with tag and confidence filters

73. ✅ Enhance Public Member Dashboard [Done: 2025-06-24]
    - Use only _sent.csv files
    - Add week/month filters
    - Plot profit curves, emoji stats, ROI by tag (sent only)
    - Hide any non-sent tips or internals
    - Add summary header: Tips, Wins, ROI, Profit.


74. ✅ **Pre-commit Hooks** — black/flake8/isort run automatically. *(2025-06-08)*
75. ✅ **Central `.env` Loader** — load env vars at script start. *(2025-06-08)*
76. ✅ **Unified CLI** — `cli/tmcli.py` with subcommands. *(2025-06-08)*
77. ✅ **GitHub Actions CI** — run tests automatically. *(2025-06-08)*
78. ✅ **Tip Dataclass** — typed representation for tips. [Done: 2025-06-25]
79. ✅ **Validate Features Utility** — check dataset vs `features.json`. *(2025-06-08)*
80. ✅ **Inference Unit Tests** — ensure `run_inference_and_select_top1.py` [Done: 2025-06-24]
81. ✅ **Model Download Helper** — `model_fetcher.py` for S3. *(2025-06-08)*
82. ✅ **Stats API** — expose JSON endpoints for ROI and tips. [Done: 2025-06-24]
83. ✅ **Telegram Sandbox** — dev channel for testing dispatch. [Done: 2025-07-07]
84. **Typed Dataset Schema** — enforce columns with `pandera`.
85. **Rolling 30-Day ROI** — auto-generated summary in logs.

86. ✅ 30-Day ROI chart in Paul's View dashboard *(2025-06-08)*

    - ✅ Initial version [Done: 2025-06-24]
    - ✅ Added tips/wins/places and strike rate [Done: 2025-06-26]
86. ✅ Removed unused `check_betfair_market_times.py` script [Done: 2025-06-23]
87. ✅ Draw Advantage tag if `draw_bias_rank` > 0.7 [Done: 2025-06-24]
88. ✅ Danger Fav history logging [Done: 2025-06-25]
89. ✅ /tip bot command to show latest horse tip [Done: 2025-06-24]
90. ✅ Smart Combo generator for doubles/trebles [Done: 2025-06-24]
91. ✅ NAP performance tracker logs to `nap_history.csv` [Done: 2025-06-25]
92. ✅ Trainer intent profiler with stable-form tags [Done: 2025-06-26]

93. Stable-level intent profiler using `trainer_intent_score.py` to combine
    trainer win-rate tracking and multiple-entry detection.

94. ✅ Script audit: keep `utils/ensure_sent_tips.py` (used in CLI and tests) [Done: 2025-06-09]
95. ✅ Time-decayed win rate weighting prioritising last 30 days over 90+ [Done: 2025-06-26]
96. ✅ Weekly ROI commentary logs with top/worst day and trend [Done: 2025-06-26]
97. ✅ `AGENTS.md` reference updated to `Docs/monster_todo.md` [Done: 2025-06-26]

98. ✅ `upload_to_s3` helper skips uploads in dev mode [Done: 2025-06-27]

99. ✅ Flake8 cleanup across core and tests [Done: 2025-07-09]
100. ✅ ROI snapshot injection integrated into pipeline [Done: 2025-07-10]
101. ✅ Telegram summaries refined [Done: 2025-07-10]

100. ✅ `--course` option to dispatch tips for a single track [Done: 2025-07-10]
pt
102. ✅ `check_tip_sanity.py` warns about low confidence or missing odds/stake [Done: 2025-07-10]

102. ✅ Log summariser script `summarise_logs.py` to review last 7 days [Done: 2025-07-11]

102. ✅ Telegram-based confidence override commands [Done: 2025-07-11]



102. ✅ Local backup validator ensures timestamped copies of root scripts [Done: 2025-07-10]

103. ✅ Pipeline script uses strict mode and skips S3 if AWS CLI missing [Done: 2025-07-12]

104. ✅ README emphasises that `--dev` (or `TM_DEV_MODE=1`) prevents real
     Telegram posts and S3 uploads during testing [Done: 2025-07-12]

105. ✅ Pipeline script handles missing args with `${1:-}` [Done: 2025-07-13]

106. ✅ tmcli pipeline works again after fixing script paths [Done: 2025-07-13]

