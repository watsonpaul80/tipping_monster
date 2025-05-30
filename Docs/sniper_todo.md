# TIPPING MONSTER TODO LIST

## Completed ✅
- [x] Daily/weekly ROI tracking based on advised stakes  
- [x] ROI calculation documentation  
- [x] Safecron Telegram failure alerts integration  
- [x] Sniper pipeline scripts: fetch, merge, detect, dispatch  
- [x] Sniper automation schedule build and load  
- [x] Volume collection from Betfair odds snapshots  
- [x] Batch dispatch of sniper alerts to Telegram (updated to 10 per batch)  

## Current Backlog
- [ ] Odds progression tracking across snapshots with visualization  
- [ ] Implement confidence tiers for steamers (High, Moderate, Low) using volume, odds drop, and form data  
- [ ] Overlay trainer & jockey form stats into sniper alerts  
- [ ] Incorporate course/distance/going profile checks for steamers  
- [ ] Train and integrate ML classifier to score steamers’ win likelihood  
- [ ] Use ML confidence scores to suppress low-quality steamers  
- [ ] Staking simulation based on confidence tiers for sniper bets  
- [ ] Expand Telegram Market Intelligence reports with enhanced context and formatting  
- [ ] Develop visual ROI dashboards and tag-based filtering (NAPs, trainer, class, etc.)  
- [ ] Monetisation tiers and private premium Telegram channels setup  
- [ ] Add LLM-generated commentary explaining picks and confidence levels  
- [ ] Implement Telegram user commands (e.g., /roi, /stats, /nap)  
- [ ] Build self-training loops using tip outcomes to improve models  
- [ ] Automate webhook actions to manage expired subscribers  
- [ ] Create intro walkthrough videos and marketing collateral  

## Infrastructure & Stability
- [ ] Full README and detailed documentation for all sniper-related scripts and automation  
- [ ] Clean deprecated and unused sniper scripts and scheduling files  
- [ ] Add automated verification to ensure snapshot files exist before running compare jobs  
- [ ] Enhance error messaging and alerting for missing data or snapshot issues  
- [ ] Implement success Telegram alerts for critical sniper pipeline steps  

## Miscellaneous
- [ ] Add better error recovery and retries in Betfair API calls  
- [ ] Add more comprehensive logging and monitoring dashboards  
- [ ] Optimize pipeline execution time and resource usage  
