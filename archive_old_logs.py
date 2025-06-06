import argparse
from datetime import datetime, timedelta
from pathlib import Path
import zipfile


def archive_logs(log_dir: Path, days: int, archive_dir: Path):
    cutoff = datetime.now() - timedelta(days=days)
    log_dir = log_dir.resolve()
    archive_dir = archive_dir.resolve()
    archive_dir.mkdir(parents=True, exist_ok=True)

    for file in log_dir.rglob("*.log"):
        if not file.is_file():
            continue
        mtime = datetime.fromtimestamp(file.stat().st_mtime)
        if mtime >= cutoff:
            continue
        rel = file.relative_to(log_dir)
        zip_path = archive_dir / f"{rel}.zip"
        zip_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(file, arcname=file.name)
        file.unlink()
        print(f"Archived {file} -> {zip_path}")


def main():
    parser = argparse.ArgumentParser(description="Archive logs older than N days into zip files")
    parser.add_argument("--log-dir", default="logs", help="Path to logs directory")
    parser.add_argument("--days", type=int, default=14, help="Archive files older than this many days")
    parser.add_argument("--archive-dir", default="logs/archive", help="Where to store zipped logs")
    args = parser.parse_args()

    archive_logs(Path(args.log_dir), args.days, Path(args.archive_dir))


if __name__ == "__main__":
    main()
