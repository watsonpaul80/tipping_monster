# 🧠 TIPPING MONSTER — PRIORITISED MASTER TODO

A living roadmap of every feature, fix, and dream for the Tipping Monster system.  
**Numbered by priority.**  
**✅ = Complete** | **🔥 = High Priority** | **🧪 = Experimental** | **💡 = Idea** | **📈 = Business** | **🔁 = Odds** | **🧠 = ML/Model**

---

## 🔥 HIGH PRIORITY (Current Sprint)

1. **ML-Based Commentary System** — tag-based smart summaries (no LLM)
2. **`.env` Secrets Refactor** — move Telegram token, AWS keys, etc. out of scripts
3. **Model v6 vs v7 Shadow Compare** — dual pipeline + logging for ROI comparison
4. **Dev Env Completion** — `Makefile`, `dev-check.sh`, log consistency
5. **Sort `logs/` Folder** — subfolders for `roi/`, `dispatch/`, `inference/`, `sniper/`
6. **Script Audit** — identify redundant scripts and prune/rename as needed
7. **`--dev` Flag Support Across Scripts** — override to prevent real S3 upload, redirect Telegram to personal channel, log to dev folder
8. **NAP Sanity Filter + Override** — block NAPs over odds cap (e.g. 20/1), allow fallback tag, optional manual override field

---

## 🛠️ MEDIUM PRIORITY (Next Sprint)

9. Suppression logic based on band ROI performance  
10. Highlight best/worst bands visually in summary  
11. Weekly retraining instead of daily (optional)  
12. Telegram `/rate` Feature — rate personal picks with ML feedback  
13. Telegram Tip Control Panel — send custom messages, full racecards, etc.  
14. Breeding Feature in Model — integrate stallion win rates, debut stats  
15. Trainer/Jockey ROI Leaderboard — daily form summary or on-demand stats  
16. All Tips Mode — dispatch full racecards (mug mode) alongside Monster Tips  
17. Passive tracking of 0.50–0.80 band ROI  
18. Activate suppression logic based on band ROI performance  
19. SHAP or feature gain per model  
20. Top 5 feature impact per tip (in .md + Telegram)  
21. Logic-based commentary block: “📉 Class Drop, 📈 In Form, Conf: 92%”  
22. Use tags + confidence + form stats for explanation  
23. Score tips by band, confidence, and value  
24. Tag top 3 per day as Premium Tips  
25. Split public vs subscriber tips via logic or tier  
26. ROI breakdown by confidence band, tip type, and tag  
27. Show top ROI tags daily  
28. Telegram control panel for config (bands, filters)  
29. Parallel model comparison (v6 vs v7)  
30. Drawdown tracking in ROI logs  

---

## 🧠 IN PROGRESS / v6 POLISH

31. Suppression logic based on band ROI performance  
32. Highlight best/worst bands visually in summary  
33. Weekly retraining instead of daily (optional)  
34. ✅ Auto-send subscriber-friendly ROI summary to Telegram channel  
> Daily + weekly summaries are now live and formatted. Sent via cron with rich Telegram formatting.

---

## 🧠 BACKLOG: v7+ FEATURES & ENHANCEMENTS

35. Passive tracking of 0.50–0.80 band ROI (no suppression)  
36. Activate suppression logic based on band ROI performance  
37. SHAP or feature gain per model  
38. Top 5 feature impact per tip (in .md + Telegram)  
39. Add logic-based commentary block: “📉 Class Drop, 📈 In Form, Conf: 92%”  
40. Use tags + confidence + form stats for explanation  
41. Score tips by band, confidence, and value  
42. Tag top 3 per day as Premium Tips  
43. Split public vs subscriber tips via logic or tier  
44. ROI breakdown by confidence band, tip type, and tag  
45. Show top ROI tags daily  
46. Telegram control panel for config (bands, filters)  
47. Parallel model comparison (v6 vs v7)  
48. Drawdown tracking in ROI logs  

---

## 🔭 STRATEGIC ENHANCEMENTS (v8+ & BEYOND)

49. Place-focused model (predict 1st–3rd)  
50. Confidence regression model (predict prob, not binary)  
51. ROI-based calibration (not just accuracy)  
52. Penalise stale horses and poor form  
53. Add weekly ROI line chart (matplotlib) to logs  
54. Include win/loss emoji outcomes in Telegram ROI  
55. Optional: highlight top winners in Telegram  
56. NAP-only output mode for casual tier  
57. Invite-only Telegram access logic  
58. Visual dashboards (Streamlit / HTML)  
59. Monetisation hooks (Stripe, Patreon, etc.)  

---

## 🔁 REALISTIC ODDS INTEGRATION

**Goal:** Improve ROI transparency by replacing inaccurate SPs with realistic odds from pre-race snapshots.

60. ✅ Build `extract_best_realistic_odds.py` to inject best odds before race  
61. ✅ Output `logs/sent_tips_YYYY-MM-DD_realistic.jsonl`  
62. ✅ Update ROI tracker to prefer realistic odds over `bf_sp`  
63. ✅ Show “Realistic Odds Mode” label in ROI summary  
64. Log delta: `realistic_odds - bf_sp` in ROI logs  
65. Optional: Show delta highlights in Telegram ROI (e.g. “💸 14/1 ➝ 4.3”)  
66. Track performance of tips with high odds delta (market steamers)  
> Paused — Steam Sniper mode is disabled for now. This will be revisited when the sniper system is rebuilt from scratch.  
67. Add `odds_delta` to ML training later as input signal  

---

## 💡 IDEAS & PIPELINE QUALITY

68. Fallback logic if `logs/sent_tips.jsonl` is missing  
69. Alert if dispatch runs but no tips are sent  
70. Alert if odds snapshot fails or returns too few runners  
71. Self-heal for missing `logs/`, retry on failure  

---

## 🧠 LEARNING FROM ODDS DELTA

**Goal:** Train Monster to learn from large market moves.

72. Calculate and store `odds_delta` (realistic - SP)  
73. Score tips based on delta + result + confidence  
74. Reward positive delta wins, penalise drifts  
75. Add `delta_tag` to messages (e.g. “🔥 Market Mover”)  
76. Use as feature or reinforcement signal in future models  

---

## 📈 BUSINESS & MONETISATION

### Phase 1: Free Launch
77. ✅ Weekly + daily ROI tracking in Telegram  
78. ✅ ROI logic documented  
79. Build basic landing page  
80. Setup `/join` or invite-link system  

### Phase 2: Trust Builder
81. Public ROI dashboard (Google Sheets / CSV)  
82. Share summaries on Reddit/forums weekly  
83. Capture emails or poll interest  
84. Trial affiliate links with tracking  

### Phase 3: Monetisation
85. Stripe/Patreon integration  
86. “Monster Premium” Telegram channel  
87. Post pinned weekly ROI + tip snapshot  
88. Sell tip packs, stats, NAPs, etc.  

### Bonus Features / Engagement
89. Add /roi, /stats, /nap bot commands  
90. Add Telegram confidence commentary  
91. Optional intro video of how Monster works  

---

## ✅ ROI SYSTEM TODO (NEW FEATURES)

92. 🔨 Build Paul's View Dashboard  
    - Create `pauls_view_dashboard.py`
    - Load all _all.csv tip logs
    - Add filters: tag, confidence, sent, NAP, trainer/jockey ROI
    - Charts: ROI over time, confidence vs ROI, tag breakdown
    - Table: unified tip sheet with all stats
    - Option to export filtered view to CSV

93. 🎯 Enhance Public Member Dashboard  
    - Use only _sent.csv files
    - Add week/month filters
    - Plot profit curves, emoji stats, ROI by tag (sent only)
    - Hide any non-sent tips or internals
    - Add summary header: Tips, Wins, ROI, Profit

---

**Legend:**  
🔥 = High Priority | 🧠 = ML/Model | 🧪 = Experimental | 💡 = Idea | 📈 = Business | 🔁 = Odds | ✅ = Complete