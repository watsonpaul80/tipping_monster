from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List

import pandas as pd
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Tipping Monster Stats API")

LOGS_DIR = Path(os.getenv("TM_LOGS_DIR", "logs"))
PRED_DIR = Path(os.getenv("TM_PRED_DIR", "predictions"))


def _latest_csv(folder: Path) -> Path | None:
    csv_files = sorted(folder.glob("*.csv"), key=lambda p: p.stat().st_mtime)
    return csv_files[-1] if csv_files else None


def _load_csv(path: Path) -> List[dict]:
    try:
        return pd.read_csv(path).to_dict(orient="records")
    except Exception as exc:  # pragma: no cover - unexpected read failure
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def _load_predictions(path: Path) -> List[dict]:
    if not path.exists():
        raise HTTPException(status_code=404, detail="Predictions not found")
    records = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            records.append(json.loads(line))
    return records


@app.get("/roi")
def get_roi():
    roi_folder = LOGS_DIR / "roi"
    latest = _latest_csv(roi_folder)
    if not latest:
        raise HTTPException(status_code=404, detail="ROI data unavailable")
    return _load_csv(latest)


@app.get("/tags")
def get_tags():
    roi_folder = LOGS_DIR / "roi"
    tag_csvs = sorted(
        roi_folder.glob("tag_roi_summary*.csv"), key=lambda p: p.stat().st_mtime
    )
    if not tag_csvs:
        raise HTTPException(status_code=404, detail="Tag ROI data unavailable")
    return _load_csv(tag_csvs[-1])


@app.get("/tips")
def get_tips():
    pred_dirs = [d for d in PRED_DIR.iterdir() if d.is_dir()]
    if not pred_dirs:
        raise HTTPException(status_code=404, detail="No predictions available")
    latest_dir = sorted(pred_dirs)[-1]
    output_file = latest_dir / "output.jsonl"
    return _load_predictions(output_file)


if __name__ == "__main__":  # pragma: no cover - manual start
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
