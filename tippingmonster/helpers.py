from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import shap
import xgboost as xgb

from .utils import repo_path, send_telegram_message, send_telegram_photo

__all__ = ["dispatch", "send_daily_roi", "generate_chart"]


def _apply_dev_env(dev: bool) -> None:
    if dev:
        os.environ["TM_DEV_MODE"] = "1"
        os.environ["TM_LOG_DIR"] = "logs/dev"


def dispatch(
    date: str,
    telegram: bool = False,
    dev: bool = False,
    course: str | None = None,
) -> None:
    """Run ``dispatch_tips.py`` for ``date``."""
    _apply_dev_env(dev)
    cmd = [sys.executable, str(repo_path("core", "dispatch_tips.py")), "--date", date]
    if telegram:
        cmd.append("--telegram")
    if dev:
        cmd.append("--dev")
    if course:
        cmd += ["--course", course]
    subprocess.run(cmd, check=True)


def send_daily_roi(date: str | None = None, dev: bool = False) -> None:
    """Send the daily ROI summary via ``send_daily_roi_summary.py``."""
    _apply_dev_env(dev)
    cmd = [sys.executable, str(repo_path("roi", "send_daily_roi_summary.py"))]
    if date:
        cmd += ["--date", date]
    if dev:
        cmd.append("--dev")
    subprocess.run(cmd, check=True)


def generate_chart(
    model_path: str,
    data_path: str | None,
    out_path: Path,
    telegram: bool = False,
) -> None:
    """Create a SHAP feature importance chart and optionally send to Telegram."""
    model = xgb.Booster()
    if model_path.endswith(".gz"):
        import gzip
        import tempfile

        with gzip.open(model_path, "rb") as f, tempfile.NamedTemporaryFile(
            delete=False
        ) as tmp:
            tmp.write(f.read())
            tmp_path = tmp.name
        model.load_model(tmp_path)
        os.unlink(tmp_path)
    else:
        model.load_model(model_path)
    if data_path is None:
        raise ValueError("data_path must be provided")
    df = pd.read_csv(data_path)
    explainer = shap.TreeExplainer(model)
    dmatrix = xgb.DMatrix(df)
    shap_values = explainer.shap_values(dmatrix)
    shap.summary_plot(shap_values, df, show=False)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    if telegram:
        send_telegram_photo(out_path)
        send_telegram_message("Model feature importance", None, None)
