import os
import requests
from pathlib import Path
import re

__all__ = [
    "repo_root",
    "repo_path",
    "logs_path",
    "predictions_path",
    "send_telegram_message",
    "calculate_profit",
]

# Base directory of the repository. Can be overridden via TM_ROOT env var.
BASE_DIR = Path(os.getenv("TM_ROOT", Path(__file__).resolve().parents[1]))

def repo_root() -> Path:
    """Return the repository root as a ``Path`` object."""
    return BASE_DIR


def repo_path(*parts: str) -> Path:
    """Join ``parts`` to the repository root and return a ``Path``."""
    return repo_root().joinpath(*parts)


def logs_path(*parts: str) -> Path:
    """Convenience helper for ``logs/`` paths relative to the repository root."""
    return repo_path("logs", *parts)


def predictions_path(date: str) -> Path:
    """Return the predictions directory for ``date``."""
    return repo_path("predictions", date)


def send_telegram_message(message: str, token: str | None = None, chat_id: str | None = None) -> None:
    """Send ``message`` to Telegram using bot ``token`` and ``chat_id``.

    The environment variables ``TELEGRAM_BOT_TOKEN`` and ``TELEGRAM_CHAT_ID``
    are used if ``token`` or ``chat_id`` are not provided.
    """
    token = token or os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    requests.post(url, data=payload, timeout=10)


def _get_place_terms(runners: int, race_name: str) -> tuple[float, int]:
    """Return place fraction and number of places for each-way bets."""
    is_handicap = "hcp" in race_name.lower()
    if is_handicap:
        if runners >= 16:
            return 0.25, 4
        if 12 <= runners <= 15:
            return 0.25, 3
    if runners >= 8:
        return 0.20, 3
    if 5 <= runners <= 7:
        return 0.25, 2
    return 0.0, 1  # Win only fallback


def calculate_profit(row) -> float:
    """Calculate profit for a single result row.

    ``row`` is expected to have the columns ``Odds``, ``Position`` and
    ``Stake`` as used in ROI tracking scripts. Other optional fields such as
    ``Runners`` and ``Race Name`` are used to determine place terms for
    each-way bets.
    """
    odds = row["Odds"]
    position = str(row["Position"]).lower()
    stake = row["Stake"]

    if odds >= 5.0:
        win_stake = 0.5
        place_stake = 0.5
        place_fraction, place_places = _get_place_terms(int(row.get("Runners", 0)), str(row.get("Race Name", "")))

        win_profit = (odds - 1) * win_stake if position == "1" else 0.0
        place_profit = ((odds * place_fraction) - 1) * place_stake if position.isdigit() and int(position) <= place_places and place_places > 1 else 0.0
        return round(win_profit + place_profit, 2)
    else:
        win_profit = (odds - 1) * stake if position == "1" else -stake
        return round(win_profit, 2)
