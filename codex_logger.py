from __future__ import annotations
import datetime
from pathlib import Path

DEFAULT_LOG = Path('logs/codex.log')

def log_action(message: str, log_path: Path | str = DEFAULT_LOG) -> Path:
    """Append a timestamped message to the Codex log file.

    Parameters
    ----------
    message : str
        Text to record in the log.
    log_path : Path | str, optional
        File path to append the message, by default ``logs/codex.log``.

    Returns
    -------
    Path
        The path to the log file that was written.
    """
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().isoformat(timespec='seconds')
    with path.open('a', encoding='utf-8') as fh:
        fh.write(f"{timestamp} {message}\n")
    return path

