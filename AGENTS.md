## 📦 Project Workflow & Agent Protocols

### ✅ General Workflow
- Use a GitHub-style workflow with feature branches, PRs, and commits tied to specific task IDs when possible.
- Run `pytest` and `pre-commit run --files <file>` on any modified files before committing.

### 🧪 Testing Guidelines
- **No Telegram posts in tests**: Use `--dev` flag or `TM_DEV=1` to suppress Telegram sends during test or dry-run sessions.
- If tests fail due to missing dependencies or external API issues (e.g., Betfair), document this in the PR or task log.

### 📝 Documentation Protocol
- Keep all `*.md` files up to date when relevant changes are made (especially `TIPPING_MONSTER_TODO.md`, `monster_overview.md`, and `CHANGELOG.md`).
- Summarise any significant system changes in `CHANGELOG.md` immediately after implementation.

### 🎨 Code Style
- Use `black` and `flake8` for formatting and linting.
- Organize imports with `isort`.
- Write clear, maintainable Python following standard best practices.

---

### 🤖 Agent Codex Responsibilities

Codex is the autonomous coding agent in this repo. It must:

- Maintain all system scripts and automation pipelines
- Respect file boundaries (scripts vs utils vs logs)
- After completing any prompt, automatically append to:
  - `CHANGELOG.md`: what changed and why (user-facing)
  - `codex_log.md`: what was requested, timestamp, and affected files (internal/dev)

Example log entry for `codex_log.md`:

```
## [2025-06-08] Add confidence suppression to dispatch_tips.py
**Prompt:** Suppress tips under 80% confidence unless band ROI is positive  
**Files Changed:** dispatch_tips.py, utils/roi_utils.py  
**Outcome:** Filtered out low-confidence underperformers from tip flow
```

---

This ensures all changes are reproducible, reviewed, and audit-proof.
