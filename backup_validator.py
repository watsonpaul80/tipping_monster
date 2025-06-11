import glob
import os
import shutil
from datetime import datetime

BACKUP_DIR = "backups"


def ensure_backup(script_path: str) -> str:
    """Ensure a timestamped backup exists for the given script."""
    base_name = os.path.splitext(os.path.basename(script_path))[0]
    pattern = os.path.join(BACKUP_DIR, f"{base_name}_*.py")
    existing = glob.glob(pattern)
    if existing:
        return f"Already backed up: {os.path.basename(existing[0])}"

    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M")
    dest = os.path.join(BACKUP_DIR, f"{base_name}_{timestamp}.py")
    shutil.copy2(script_path, dest)
    return f"Backup created: {os.path.basename(dest)}"


def main() -> None:
    scripts = [f for f in os.listdir(".") if f.endswith(".py")]
    reports = []
    for script in scripts:
        reports.append(ensure_backup(script))
    for report in reports:
        print(report)


if __name__ == "__main__":
    main()
