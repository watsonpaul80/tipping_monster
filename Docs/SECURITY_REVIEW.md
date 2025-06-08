# Security Review

This document highlights potential security issues in the repository and provides recommendations.

## Findings

- **Secrets exposed in version control**
  - The file `monstertweeter/.env` contains Twitter API keys and access tokens.
  - `rpscrape/scripts/daily_results.sh` hard codes database host, user and password.
- **Shell invocation**
  - `rpscrape/scripts/utils/argparser.py` uses `os.system()` which can lead to shell injection.
- **Archive extraction**
  - `run_inference_and_select_top1.py` extracts tar files using `tarfile.extractall()` without validation.
- **HTTP requests without timeout**
  - Several scripts previously called `requests.get` or `requests.post` without a `timeout` argument, e.g. `roi_tracker_advised.py` and `scripts/morning_digest.py`. These have been updated to use a 10‑second timeout.

## Recommendations

1. Remove sensitive credentials from the repository and rotate them immediately.
2. Store credentials in environment variables or a secure secrets manager and add the files to `.gitignore`.
3. Replace `os.system` calls with the `subprocess` module or sanitize all inputs.
4. Validate archive contents before extraction or extract safely using `tarfile` members.
5. Add explicit timeouts to all network requests to avoid hanging connections.
6. Consider adding `bandit` or similar tools to the CI pipeline.
7. Use the `tippingmonster.send_telegram_message` helper for any Telegram alerts
   so `TM_DEV_MODE` is honored.

