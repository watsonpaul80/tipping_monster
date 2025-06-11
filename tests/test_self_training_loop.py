from pathlib import Path

from self_training_loop import gather_roi_logs


def test_gather_roi_logs(tmp_path: Path):
    base = tmp_path / "logs"
    (base / "roi").mkdir(parents=True)
    (base / "tips_results_a_advised.csv").write_text("a")
    (base / "roi" / "tips_results_b_advised.csv").write_text("b")

    files = gather_roi_logs(str(base))
    assert len(files) == 2
    assert any(f.endswith("tips_results_a_advised.csv") for f in files)
    assert any(f.endswith("tips_results_b_advised.csv") for f in files)
