from __future__ import annotations

import pandas as pd

BANDS = [
    (0.50, 0.60, "0.50–0.60"),
    (0.60, 0.70, "0.60–0.70"),
    (0.70, 0.80, "0.70–0.80"),
    (0.80, 0.90, "0.80–0.90"),
    (0.90, 1.00, "0.90–1.00"),
    (0.99, 1.01, "0.99–1.01"),
]


def get_band_label(conf: float) -> str | None:
    """Return the band label for conf or None if out of range."""
    if pd.isna(conf):
        return None
    for low, high, label in BANDS:
        if low <= conf < high:
            return label
    return None


def is_band_profitable(confidence: float, roi_df: pd.DataFrame) -> bool:
    """Return True if the confidence band shows positive ROI in roi_df."""
    band = get_band_label(confidence)
    if not band or roi_df is None or roi_df.empty:
        return False
    if "Confidence Bin" not in roi_df.columns:
        return False
    df = roi_df[roi_df["Confidence Bin"] == band]
    if df.empty:
        return False
    tips = pd.to_numeric(df["Tips"], errors="coerce").sum()
    pnl = pd.to_numeric(df["Win PnL"], errors="coerce").sum()
    roi = pnl / tips if tips else 0.0
    return roi > 0.0
