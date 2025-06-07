#!/usr/bin/env python3
"""Generate a model drift report from SHAP feature importances."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import boto3
import pandas as pd
from scipy.stats import spearmanr


def load_shap_csv(
    date: str,
    local_dir: Path,
    bucket: Optional[str] = None,
    prefix: str = "shap",
    s3_client: Optional[boto3.client] = None,
) -> Optional[pd.DataFrame]:
    """Load a ``<date>_shap.csv`` file from ``local_dir`` or S3.

    The CSV must have ``feature`` and ``importance`` columns.
    """
    local_path = local_dir / f"{date}_shap.csv"
    if local_path.exists():
        return pd.read_csv(local_path)
    if bucket and s3_client:
        key = f"{prefix}/{date}_shap.csv"
        tmp_path = local_dir / f"tmp_{date}_shap.csv"
        try:
            local_dir.mkdir(parents=True, exist_ok=True)
            s3_client.download_file(bucket, key, str(tmp_path))
            return pd.read_csv(tmp_path)
        except Exception as exc:  # pragma: no cover - network errors vary
            print(f"⚠️ Could not fetch {key}: {exc}")
    return None


def compare_rankings(
    dfs: list[pd.DataFrame],
    dates: list[str],
    top_n: int = 20,
    threshold: float = 0.9,
) -> str:
    """Return a markdown summary comparing feature importance rankings."""
    lines = [f"## Model Drift Report ({dates[0]} – {dates[-1]})"]

    baseline = dfs[0].sort_values("importance", ascending=False).head(top_n)
    baseline_rank = {f: i for i, f in enumerate(baseline["feature"].tolist())}

    for df, date in zip(dfs[1:], dates[1:]):
        cur = df.sort_values("importance", ascending=False).head(top_n)
        cur_features = cur["feature"].tolist()

        ranks_base = []
        ranks_cur = []
        for feat, base_idx in baseline_rank.items():
            if feat in cur_features:
                ranks_base.append(base_idx)
                ranks_cur.append(cur_features.index(feat))

        corr = float("nan")
        if len(ranks_base) > 1:
            corr, _ = spearmanr(ranks_base, ranks_cur)

        drift_flag = " ❗" if corr < threshold else ""
        lines.append(f"- {date}: Spearman {corr:.2f}{drift_flag}")

        if drift_flag:
            shifts = []
            for feat, base_idx in baseline_rank.items():
                if feat in cur_features:
                    diff = cur_features.index(feat) - base_idx
                    if abs(diff) >= 5:
                        shifts.append(f"{feat} ({diff:+d})")
            new_feats = [f for f in cur_features if f not in baseline_rank]
            if shifts:
                lines.append(f"  - Rank shifts: {', '.join(shifts)}")
            if new_feats:
                lines.append(f"  - New top features: {', '.join(new_feats)}")
    return "\n".join(lines) + "\n"


def generate_report(
    days: int = 7,
    local_dir: str = "shap",
    bucket: Optional[str] = None,
    prefix: str = "shap",
    out_md: str = "logs/model_drift_report.md",
) -> Path:
    """Create a drift report and return the markdown file path."""
    s3_client = boto3.client("s3") if bucket else None
    local = Path(local_dir)
    today = datetime.utcnow().date()

    dfs: list[pd.DataFrame] = []
    dates: list[str] = []
    for i in range(days):
        date_obj = today - timedelta(days=days - i - 1)
        date_str = date_obj.strftime("%Y-%m-%d")
        df = load_shap_csv(date_str, local, bucket, prefix, s3_client)
        if df is not None:
            dfs.append(df)
            dates.append(date_str)

    if not dfs:
        raise FileNotFoundError("No SHAP CSVs found")

    md = compare_rankings(dfs, dates)
    out_path = Path(out_md)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md)
    return out_path


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Detect model drift via SHAP rankings")
    parser.add_argument(
        "--days", type=int, default=7, help="How many past days to analyse"
    )
    parser.add_argument(
        "--local-dir", default="shap", help="Directory with <date>_shap.csv files"
    )
    parser.add_argument("--bucket", help="S3 bucket containing SHAP CSVs")
    parser.add_argument("--prefix", default="shap", help="S3 prefix for SHAP CSVs")
    parser.add_argument(
        "--out-md", default="logs/model_drift_report.md", help="Markdown output path"
    )
    args = parser.parse_args(argv)

    out = generate_report(
        days=args.days,
        local_dir=args.local_dir,
        bucket=args.bucket,
        prefix=args.prefix,
        out_md=args.out_md,
    )
    print(f"✅ Report written to {out}")


if __name__ == "__main__":
    main()
