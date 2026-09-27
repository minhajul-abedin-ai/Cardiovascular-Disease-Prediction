from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.request import urlopen

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

EXPECTED_COLUMNS = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal", "target",
]

DATA_MIRRORS = [
    "https://raw.githubusercontent.com/GehadGad/Heart-disease-dataset/main/heart.csv",
    "https://raw.githubusercontent.com/amann2802/Heart-disease-prediction-ML-pipeline/main/heart.csv",
]


@dataclass(frozen=True)
class DataAudit:
    rows_before: int
    rows_after_dedup: int
    duplicate_rows: int
    missing_values: int


def validate_columns(df: pd.DataFrame) -> None:
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    extra = [c for c in df.columns if c not in EXPECTED_COLUMNS]
    if missing or extra:
        raise ValueError(
            f"Unexpected schema. Missing={missing or 'none'}, extra={extra or 'none'}"
        )


def download_dataset(destination: str | Path) -> Path:
    """Download the 1,025-row heart.csv used by the original coursework.

    The function tries public mirrors of the Kaggle/UCI-derived dataset and
    validates the resulting schema. Raw data are downloaded at runtime rather
    than relicensed by this repository.
    """
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []

    for url in DATA_MIRRORS:
        try:
            with urlopen(url, timeout=30) as response:
                payload = response.read()
            destination.write_bytes(payload)
            df = pd.read_csv(destination)
            validate_columns(df)
            if len(df) != 1025:
                raise ValueError(f"Expected 1025 rows, downloaded {len(df)}")
            return destination
        except Exception as exc:  # noqa: BLE001 - report all mirror failures
            errors.append(f"{url}: {exc}")
            if destination.exists():
                destination.unlink()

    raise RuntimeError("Could not download dataset.\n" + "\n".join(errors))


def load_raw_data(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {path}. Run: python scripts/download_dataset.py"
        )
    df = pd.read_csv(path)
    validate_columns(df)
    return df


def audit_and_deduplicate(df: pd.DataFrame) -> tuple[pd.DataFrame, DataAudit]:
    validate_columns(df)
    duplicates = int(df.duplicated().sum())
    missing_values = int(df.isna().sum().sum())
    cleaned = df.drop_duplicates().reset_index(drop=True)
    return cleaned, DataAudit(
        rows_before=len(df),
        rows_after_dedup=len(cleaned),
        duplicate_rows=duplicates,
        missing_values=missing_values,
    )


class IQRClipper(BaseEstimator, TransformerMixin):
    """Train-fitted IQR clipping for selected numeric columns.

    Unlike the original assignment notebook, this transformer learns clipping
    bounds only from the training fold, so test/CV information does not affect
    preprocessing thresholds.
    """

    def __init__(self, columns: Iterable[str] = ("trestbps", "chol", "thalach")):
        self.columns = tuple(columns)

    def fit(self, X: pd.DataFrame, y=None):
        X = self._as_frame(X)
        self.feature_names_in_ = list(X.columns)
        self.bounds_: dict[str, tuple[float, float]] = {}
        for col in self.columns:
            if col not in X.columns:
                raise ValueError(f"IQR column {col!r} is missing from features")
            q1 = float(X[col].quantile(0.25))
            q3 = float(X[col].quantile(0.75))
            iqr = q3 - q1
            self.bounds_[col] = (q1 - 1.5 * iqr, q3 + 1.5 * iqr)
        return self

    def transform(self, X: pd.DataFrame):
        X = self._as_frame(X).copy()
        for col, (lower, upper) in self.bounds_.items():
            X[col] = X[col].clip(lower=lower, upper=upper)
        return X

    def get_feature_names_out(self, input_features=None):
        return np.asarray(self.feature_names_in_, dtype=object)

    @staticmethod
    def _as_frame(X) -> pd.DataFrame:
        if isinstance(X, pd.DataFrame):
            return X
        raise TypeError("IQRClipper expects a pandas DataFrame so column names are preserved")
