import os
import shutil
from pathlib import Path

import requests

__all__ = [
    "repo_root",
    "repo_path",
    "logs_path",
    "predictions_path",
    "in_dev_mode",
    "send_telegram_message",
    "send_telegram_photo",
    "load_xgb_model",
    "calculate_profit",
    "get_place_terms",
    "tip_has_tag",
    "upload_to_s3",
]

# Base directory of the repository. Can be overridden via TM_ROOT env var.
BASE_DIR = Path(os.getenv("TM_ROOT", Path(__file__).resolve().parents[1]))


def in_dev_mode() -> bool:
    return os.getenv("TM_DEV_MODE") == "1"


def repo_root() -> Path:
    return BASE_DIR


def repo_path(*parts: str) -> Path:
    return repo_root().joinpath(*parts)


def logs_path(*parts: str) -> Path:
    base = "logs/dev" if in_dev_mode() else "logs"
    return repo_path(base, *parts)


def predictions_path(date: str) -> Path:
    return repo_path("predictions", date)


def upload_to_s3(local_path: str | Path, bucket: str, key: str) -> None:
    """Upload ``local_path`` to ``bucket``/``key`` unless in dev mode."""
    if in_dev_mode():
        print(f"[DEV] Skipping S3 upload to s3://{bucket}/{key}")
        return
    import boto3

    boto3.client("s3").upload_file(str(local_path), bucket, key)


def send_telegram_message(
    message: str, token: str | None = None, chat_id: str | None = None
) -> None:
    if in_dev_mode():
        log_file = logs_path("telegram.log")
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(message + "\n")
        print(f"[DEV] Telegram message suppressed: {message}")
        return

    token = token or os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
    if os.getenv("TM_DEV"):
        chat_id = os.getenv("TELEGRAM_DEV_CHAT_ID", chat_id)
    if not token or not chat_id:
        raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    resp = requests.post(url, data=payload, timeout=10)
    if resp.status_code >= 400:
        msg = f"Telegram API error {resp.status_code}: {resp.text}"
        if in_dev_mode():
            print(f"[DEV] {msg}")
        else:
            raise RuntimeError(msg)


def send_telegram_photo(
    photo: Path | str,
    caption: str = "",
    token: str | None = None,
    chat_id: str | None = None,
) -> None:
    if in_dev_mode():
        photo_path = Path(photo)
        dest = logs_path(photo_path.name)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(photo_path, dest)

        log_file = logs_path("telegram.log")
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(caption + "\n")
        print(f"[DEV] Telegram photo suppressed: {photo_path}")
        return

    token = token or os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
    if os.getenv("TM_DEV"):
        chat_id = os.getenv("TELEGRAM_DEV_CHAT_ID", chat_id)
    if not token or not chat_id:
        raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set")

    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    with open(photo, "rb") as f:
        files = {"photo": f}
        data = {"chat_id": chat_id, "caption": caption, "parse_mode": "Markdown"}
        resp = requests.post(url, data=data, files=files, timeout=10)
    if resp.status_code >= 400:
        msg = f"Telegram API error {resp.status_code}: {resp.text}"
        if in_dev_mode():
            print(f"[DEV] {msg}")
        else:
            raise RuntimeError(msg)


def _get_place_terms(runners: int, race_name: str) -> tuple[float, int]:
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


def get_place_terms(row: dict) -> tuple[float, int]:
    """Return each-way place fraction and number of places for a race."""
    try:
        runners = int(row.get("Runners", 0))
        race_name = str(row.get("Race Name", ""))
        return _get_place_terms(runners, race_name)
    except Exception:
        return 0.0, 1


def calculate_profit(row) -> float:
    odds = row["Odds"]
    position = str(row["Position"]).lower()
    stake = row["Stake"]

    if odds >= 5.0:
        win_stake = 0.5
        place_stake = 0.5
        place_fraction, place_places = get_place_terms(row)

        win_profit = (odds - 1) * win_stake if position == "1" else 0.0
        place_profit = (
            ((odds * place_fraction) - 1) * place_stake
            if position.isdigit() and int(position) <= place_places and place_places > 1
            else 0.0
        )
        return round(win_profit + place_profit, 2)
    else:
        win_profit = (odds - 1) * stake if position == "1" else -stake
        return round(win_profit, 2)


def tip_has_tag(tip: dict, tag: str) -> bool:
    """Return True if the tip's tags include ``tag`` (case-insensitive substring)."""
    tag_lower = tag.lower()
    return any(tag_lower in str(t).lower() for t in tip.get("tags", []))


def load_xgb_model(model_path: str):
    """Return an :class:`xgboost.XGBClassifier` from ``model_path``.

    Supports plain ``.bst`` files and gzip-compressed ``.bst.gz`` files.
    """
    import gzip
    import tempfile

    import xgboost as xgb

    model = xgb.XGBClassifier()
    if model_path.endswith(".gz"):
        with gzip.open(model_path, "rb") as f, tempfile.NamedTemporaryFile(
            suffix=".bst", delete=False
        ) as tmp:
            tmp.write(f.read())
            tmp_path = tmp.name
        model.load_model(tmp_path)
        os.unlink(tmp_path)
    else:
        model.load_model(model_path)
    return model
