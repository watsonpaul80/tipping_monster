# 🧠 TIPPING MONSTER SYSTEM DOCS

This documentation set covers everything about the **Tipping Monster** project — a fully automated machine learning tip engine for UK/IRE racing.

## 📄 Files Included

- `monster_overview.md`: Full overview of the main ML pipeline, tip logic, and automation.
- `monster_todo.md`: Task tracker for main tipping logic including ROI, model training, and Telegram output.
- `sniper_overview.md`: Description of Steam Sniper logic, snapshot timing, detection, and Telegram output.
- `sniper_todo.md`: Task tracker for Steam Sniper features, scoring, and automation ideas.

Built by Paul. Maintained by Monster. Improved by chaos. 🧠🐎

## ⚙️ Configuration

This project uses a `.env` file to manage environment-specific configurations and secrets, such as API keys and credentials.

### Setup Instructions:

1.  **Copy the Example File:**
    In the root of the repository, you will find a file named `.env.example`. Make a copy of this file and name it `.env`:
    ```bash
    cp .env.example .env
    ```

2.  **Populate Credentials:**
    Open the `.env` file with a text editor and fill in your actual credentials and configuration values for each variable listed. For example:
    ```env
    TELEGRAM_BOT_TOKEN=your_actual_telegram_bot_token_here
    BF_USERNAME=your_betfair_username
    # ... and so on for all variables
    ```

3.  **Git Ignore:**
    The `.env` file is included in `.gitignore`, so your actual secrets will not be committed to the repository. **Never commit your `.env` file.**

4.  **Dependencies:**
    Python scripts in this project use the `python-dotenv` library (added to `requirements.txt`) to load these environment variables from the `.env` file automatically. Shell scripts may source the `.env` file directly if configured to do so.