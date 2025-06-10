import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_dev_check_runs_from_repo_root(tmp_path):
    env_file = ROOT / ".env"
    venv_dir = ROOT / ".venv"
    created_env = False
    created_venv = False
    orig_dev = os.environ.pop("TM_DEV_MODE", None)
    if not env_file.exists():
        env_file.write_text("TEST=1")
        created_env = True
    if not venv_dir.exists():
        venv_dir.mkdir()
        created_venv = True
    env = os.environ.copy()
    env["VIRTUAL_ENV"] = str(venv_dir)
    try:
        subprocess.run(
            ["bash", str(ROOT / "utils" / "dev-check.sh")], check=True, env=env
        )
    finally:
        if created_env:
            env_file.unlink()
        if created_venv:
            venv_dir.rmdir()
        if orig_dev is not None:
            os.environ["TM_DEV_MODE"] = orig_dev
