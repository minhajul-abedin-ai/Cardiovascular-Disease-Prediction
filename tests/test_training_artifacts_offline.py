"""Offline end-to-end training contract using synthetic, nonclinical records.

The training entry point's expensive Random Forest search is reduced to one candidate
for this integration test; the training, evaluation, and serialization paths
remain real. No dataset download is performed.
"""
import json
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.model_selection import GridSearchCV as RealGridSearchCV

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import train
from data import EXPECTED_COLUMNS


def test_training_writes_loadable_artifacts_offline(tmp_path, monkeypatch):
    rows = []
    for i in range(100):
        rows.append({
            "age": 35 + i % 40, "sex": i % 2, "cp": i % 4,
            "trestbps": 105 + i % 50, "chol": 170 + i % 100,
            "fbs": (i // 3) % 2, "restecg": i % 3,
            "thalach": 100 + i % 90, "exang": (i // 2) % 2,
            "oldpeak": float(i % 20) / 10, "slope": i % 3,
            "ca": i % 4, "thal": 2 + i % 2,
            "target": int(i % 5 in (0, 1)),
        })
    frame = pd.DataFrame(rows, columns=EXPECTED_COLUMNS)
    csv_path = tmp_path / "synthetic.csv"
    frame.to_csv(csv_path, index=False)
    output = tmp_path / "artifacts"

    def fast_grid_search(*args, **kwargs):
        kwargs["param_grid"] = {
            "model__n_estimators": [10],
            "model__max_depth": [5],
            "model__min_samples_split": [2],
            "model__min_samples_leaf": [1],
        }
        kwargs["n_jobs"] = 1
        return RealGridSearchCV(*args, **kwargs)

    monkeypatch.setattr(train, "GridSearchCV", fast_grid_search)
    result = train.run(csv_path, output)

    assert result["metadata"]["train_rows"] == 80
    assert result["metadata"]["test_rows"] == 20
    assert set(result["metrics"]) == {"logistic_regression", "random_forest_tuned"}
    assert (output / "model_metrics.csv").is_file()
    metrics = pd.read_csv(output / "model_metrics.csv", index_col=0)
    assert set(metrics.index) == set(result["metrics"])
    metadata = json.loads((output / "run_metadata.json").read_text(encoding="utf-8"))
    assert metadata["data_audit"]["rows_before"] == 100
    assert metadata["rf_best_params"]["model__n_estimators"] == 10

    features = frame.drop(columns="target").iloc[:3]
    for name in result["metrics"]:
        model_path = output / f"{name}.joblib"
        assert model_path.stat().st_size > 0
        predictions = joblib.load(model_path).predict(features)
        assert len(predictions) == 3
        assert set(predictions).issubset({0, 1})
        assert (output / f"{name}_group_metrics_by_sex.csv").is_file()
        assert (output / f"{name}_confusion_matrix.png").stat().st_size > 0
        assert (output / f"{name}_roc.png").stat().st_size > 0
