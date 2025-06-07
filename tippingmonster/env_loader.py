from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv


def load_env() -> None:
    """Load environment variables from a ``.env`` file at the repo root."""
    repo_root = Path(os.getenv("TM_ROOT", Path(__file__).resolve().parents[1]))
    env_path = repo_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)


__all__ = ["load_env"]

