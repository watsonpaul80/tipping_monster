import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from model_drift_report import load_shap_csv


class FakeS3Client:
    def __init__(self, src: Path):
        self.src = src

    def download_file(
        self, bucket: str, key: str, dest: str
    ) -> None:  # pragma: no cover - simple copy
        Path(dest).write_bytes(self.src.read_bytes())


def test_load_shap_cleanup(tmp_path):
    src = tmp_path / "src.csv"
    pd.DataFrame({"feature": ["A"], "importance": [1.0]}).to_csv(src, index=False)

    df = load_shap_csv(
        "2025-06-05",
        tmp_path,
        bucket="b",
        prefix="shap",
        s3_client=FakeS3Client(src),
    )

    assert df.iloc[0]["feature"] == "A"
    assert not (tmp_path / "tmp_2025-06-05_shap.csv").exists()
