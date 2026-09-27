import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from data import EXPECTED_COLUMNS
from train import build_logistic_pipeline, build_rf_pipeline


def make_training_data(n=80):
    rows = []
    for i in range(n):
        rows.append(
            {
                "age": 35 + (i % 40),
                "sex": i % 2,
                "cp": i % 4,
                "trestbps": 105 + (i % 50),
                "chol": 170 + (i % 100),
                "fbs": (i // 3) % 2,
                "restecg": i % 3,
                "thalach": 100 + (i % 90),
                "exang": (i // 2) % 2,
                "oldpeak": float(i % 20) / 10,
                "slope": i % 3,
                "ca": i % 4,
                "thal": 2 + (i % 2),
                "target": int((i % 5) in (0, 1)),
            }
        )
    df = pd.DataFrame(rows, columns=EXPECTED_COLUMNS)
    return df.drop(columns="target"), df["target"]


def test_logistic_pipeline_fits_and_predicts():
    X, y = make_training_data()
    model = build_logistic_pipeline()
    model.fit(X, y)
    pred = model.predict(X.iloc[:5])
    assert len(pred) == 5


def test_rf_pipeline_fits_and_predicts():
    X, y = make_training_data()
    model = build_rf_pipeline()
    model.fit(X, y)
    pred = model.predict(X.iloc[:5])
    assert len(pred) == 5
