import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from data import EXPECTED_COLUMNS, IQRClipper, audit_and_deduplicate, validate_columns


def sample_frame() -> pd.DataFrame:
    rows = []
    for i in range(20):
        rows.append(
            {
                "age": 40 + i,
                "sex": i % 2,
                "cp": i % 4,
                "trestbps": 110 + i,
                "chol": 180 + 3 * i,
                "fbs": i % 2,
                "restecg": i % 3,
                "thalach": 120 + i,
                "exang": i % 2,
                "oldpeak": float(i % 5) / 2,
                "slope": i % 3,
                "ca": i % 4,
                "thal": 2 + (i % 2),
                "target": i % 2,
            }
        )
    rows.append(rows[0].copy())
    return pd.DataFrame(rows, columns=EXPECTED_COLUMNS)


def test_schema_and_deduplication():
    df = sample_frame()
    validate_columns(df)
    clean, audit = audit_and_deduplicate(df)
    assert audit.rows_before == 21
    assert audit.duplicate_rows == 1
    assert audit.rows_after_dedup == 20
    assert len(clean) == 20


def test_iqr_clipper_caps_outlier():
    df = sample_frame().drop(columns="target").drop_duplicates().reset_index(drop=True)
    df.loc[0, "chol"] = 5000
    clipper = IQRClipper(columns=["chol"])
    transformed = clipper.fit_transform(df)
    assert np.isfinite(transformed["chol"]).all()
    assert transformed["chol"].max() < 5000
