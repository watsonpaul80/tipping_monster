#!/usr/bin/env python3
"""Archive old log files into dated zip archives.

This utility compresses any files under ``logs/`` older than a given
number of days and moves them into ``logs/archive/``.
"""
from __future__ import annotations

import argparse
import zipfile
from datetime import datetime, timedelta
from pathlib import Path


def archive_old_logs(log_dir: Path = Path("logs"), days: int = 14) -> Path | None:
    """Compress and remove logs older than ``days`` days.

    Parameters
    ----------
    log_dir : Path
        Directory containing log files.
    days : int
        Age threshold in days. Files older than this will be archived.

    Returns
    -------
    Path | None
        Path to the created archive, or ``None`` if nothing was archived.
    """
    archive_dir = log_dir / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    cutoff = datetime.now() - timedelta(days=days)
    to_archive: list[Path] = []
    for path in log_dir.rglob("*"):
        if path.is_file() and archive_dir not in path.parents:
            if datetime.fromtimestamp(path.stat().st_mtime) < cutoff:
                to_archive.append(path)

    if not to_archive:
        return None

    archive_path = archive_dir / f"logs_{datetime.now():%Y-%m-%d}.zip"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file in to_archive:
            zf.write(file, file.relative_to(log_dir))
            file.unlink()

    return archive_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Archive old log files")
    parser.add_argument("--days", type=int, default=14, help="Days threshold")
    parser.add_argument("--log-dir", default="logs", help="Log directory")
    args = parser.parse_args()
    archive_old_logs(Path(args.log_dir), args.days)


if __name__ == "__main__":
    main()
