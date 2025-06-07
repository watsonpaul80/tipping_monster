# Guidelines for Codex Agents

The project uses GitHub-style workflow with pre-commit hooks and automated tests.

* **Testing**: Run `pytest` and `pre-commit run --files <file>` on changed files before committing. If tests fail due to missing dependencies or network issues, note this in the PR description.
* **No Telegram Posts in Tests**: Never send Telegram messages during testing. Use the `--dev` flag or `TM_DEV=1` to avoid accidental posts.
* **Documentation**: Keep all `*.md` files up to date when relevant changes are made.
* **Style**: Use the Black code formatter and standard Python best practices.

