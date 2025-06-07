import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.ensure_sent_tips import ensure_sent_tips


def test_ensure_creates_file(tmp_path):
    date = "2025-06-07"
    pred_dir = tmp_path / "predictions" / date
    pred_dir.mkdir(parents=True)
    (pred_dir / "tips_with_odds.jsonl").write_text("tip1\n")
    os.chdir(tmp_path)
    result = ensure_sent_tips(date)
    sent = tmp_path / "logs/dispatch" / f"sent_tips_{date}.jsonl"
    assert result.resolve() == sent
    assert sent.exists()


def test_ensure_skips_if_exists(tmp_path):
    date = "2025-06-07"
    dispatch = tmp_path / "logs/dispatch"
    dispatch.mkdir(parents=True)
    sent = dispatch / f"sent_tips_{date}.jsonl"
    sent.write_text("existing")
    os.chdir(tmp_path)
    result = ensure_sent_tips(date)
    assert result.resolve() == sent
    assert sent.read_text() == "existing"
