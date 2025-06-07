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

2. **`.env` Secrets Refactor** — move Telegram token, AWS keys, etc. out of scripts

3. **Model v6 vs v7 Shadow Compare** — dual pipeline + logging for ROI comparison

4. **Dev Env Completion** — `Makefile`, `dev-check.sh`, log consistency

5. ✅ **Sort `logs/` Folder** — subfolders for `roi/`, `dispatch/`, `inference/`, `sniper/`

6. **Script Audit** — identify redundant scripts and prune/rename as needed

7. ✅ **`--dev` Flag Support Across Scripts** — override to prevent real S3 upload, redirect Telegram to personal channel, log to dev folder

8. **NAP Sanity Filter + Override** — block NAPs over odds cap (e.g. 20/1), allow fallback tag, optional manual override field

---

## 🛠️ MEDIUM PRIORITY (Next Sprint)

9. Suppression logic based on band ROI performance  
10. Highlight best/worst bands visually in summary  
11. Weekly retraining instead of daily (optional)  
12. Telegram `/rate` Feature — rate personal picks with ML feedback  
13. Telegram Tip Control Panel — send custom messages, full racecards, etc.  
14. 🟡 *Removed for now* – breeding logic too hard to track without structured data  
15. Trainer/Jockey ROI Leaderboard — daily form summary or on-demand stats  
16. All Tips Mode — dispatch full racecards (mug mode) alongside Monster Tips  
17. SHAP or feature gain per model  
18. Top 5 feature impact per tip (in .md + Telegram)  
19. Logic-based commentary block: “📉 Class Drop, 📈 In Form, Conf: 92%”  
20. Use tags + confidence + form stats for explanation  
21. Score tips by band, confidence, and value  
22. Tag top 3 per day as Premium Tips  
23. Split public vs subscriber tips via logic or tier  
24. ROI breakdown by confidence band, tip type, and tag  
25. Show top ROI tags daily  
26. Telegram control panel for config (bands, filters)  
27. Parallel model comparison (v6 vs v7)  
28. Drawdown tracking in ROI logs

---

## 🔭 STRATEGIC ENHANCEMENTS (v8+ & BEYOND)

29. Place-focused model (predict 1st–3rd)  
30. Confidence regression model (predict prob, not binary)  
31. ROI-based calibration (not just accuracy)  
32. Penalise stale horses and poor form  
33. Add weekly ROI line chart (matplotlib) to logs  
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
46. Track high-delta tips separately (paused due to sniper being disabled)  
47. Add `odds_delta` to ML training as signal

---

## 💡 IDEAS & PIPELINE QUALITY

48. ✅ Fallback logic if `logs/sent_tips.jsonl` is missing
49. ✅ Alert if dispatch runs but no tips are sent
50. Alert if odds snapshot fails or returns too few runners  
51. Self-heal for missing logs, retry on failure

### 🧼 Log Management Enhancements (User Suggested)

* [x] [#062] Auto-archive old logs into `.zip` files (e.g. logs older than 14 days)
* [x] [#063] Add `logs/healthcheck.log` to flag missing files (e.g., snapshot, results, tips)
* [x] [#064] Stream `logs/roi/` and `logs/dispatch/` (formerly `logs/roi_logs/` and `logs/dispatch_logs/`) to S3 daily for backup
* [x] [#065] Add daily check script to verify all expected logs were created and non-empty

---

## 🧠 LEARNING FROM ODDS DELTA

52. ✅ Calculate and store `odds_delta` (realistic - SP)  
53. Score tips based on delta + result + confidence  
54. Reward positive delta wins, penalise drifts  
55. Add `delta_tag` to messages (e.g. “🔥 Market Mover”)  
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
69. Add /roi, /stats, /nap bot commands  
70. Add Telegram confidence commentary  
71. Optional intro video of how Monster works

---

## ✅ ROI SYSTEM TODO (NEW FEATURES)

72. 🔨 Build Paul's View Dashboard  
    - Create `pauls_view_dashboard.py`
    - Load all _all.csv tip logs
    - Add filters: tag, confidence, sent, NAP, trainer/jockey ROI
    - Charts: ROI over time, confidence vs ROI, tag breakdown
    - Table: unified tip sheet with all stats
    - Option to export filtered view to CSV

73. 🎯 Enhance Public Member Dashboard  
    - Use only _sent.csv files  
    - Add week/month filters  
    - Plot profit curves, emoji stats, ROI by tag (sent only)  
    - Hide any non-sent tips or internals  
    - Add summary header: Tips, Wins, ROI, Profit.


74. **Pre-commit Hooks** — black/flake8/isort run automatically.
75. **Central `.env` Loader** — load env vars at script start.
76. **Unified CLI** — `tmcli.py` with subcommands.
77. **GitHub Actions CI** — run tests automatically.
78. **Tip Dataclass** — typed representation for tips.
79. **Validate Features Utility** — check dataset vs `features.json`.
80. **Inference Unit Tests** — ensure `run_inference_and_select_top1.py`.
81. **Model Download Helper** — `model_fetcher.py` for S3.
82. **Stats API** — expose JSON endpoints for ROI and tips.
83. **Telegram Sandbox** — dev channel for testing dispatch.
84. **Typed Dataset Schema** — enforce columns with `pandera`.
85. **Rolling 30-Day ROI** — auto-generated summary in logs.
