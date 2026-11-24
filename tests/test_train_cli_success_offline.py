"""Offline successful CLI subprocess smoke test with bounded hyperparameter search.

The subprocess executes src/train.py and argparse normally. A temporary
sitecustomize module limits the expensive RF grid to one candidate for CI.
No real patient data or network access is required.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ENTRYPOINT = ROOT / "src" / "train.py"


def test_cli_trains_and_writes_reloadable_models(tmp_path):
    rows = [
        {
            "age": 35 + i % 40, "sex": i % 2, "cp": i % 4,
            "trestbps": 105 + i % 50, "chol": 170 + i % 100,
            "fbs": (i // 3) % 2, "restecg": i % 3,
            "thalach": 100 + i % 90, "exang": (i // 2) % 2,
            "oldpeak": float(i % 20) / 10, "slope": i % 3,
            "ca": i % 4, "thal": 2 + i % 2,
            "target": int(i % 5 in (0, 1)),
        }
        for i in range(100)
    ]
    data = pd.DataFrame(rows)
    dataset = tmp_path / "synthetic.csv"
    output = tmp_path / "artifacts"
    data.to_csv(dataset, index=False)

    # Python imports sitecustomize on startup when present on PYTHONPATH.
    # Restrict only the RF grid search; actual fit, metrics, and serialization
    # still execute in the separate Python process.
    startup = tmp_path / "startup"
    startup.mkdir()
    (startup / "sitecustomize.py").write_text(
        "from sklearn.model_selection import GridSearchCV\n"
        "_original = GridSearchCV.__init__\n"
        "def _bounded(self, estimator, param_grid, **kwargs):\n"
        "    if hasattr(estimator, 'named_steps') and 'model' in estimator.named_steps:\n"
        "        param_grid = {'model__n_estimators': [10], "
        "'model__max_depth': [5], "
        "'model__min_samples_split': [2], "
        "'model__min_samples_leaf': [1]}\n"
        "        kwargs['n_jobs'] = 1\n"
        "    return _original(self, estimator, param_grid, **kwargs)\n"
        "GridSearchCV.__init__ = _bounded\n",
        encoding="utf-8",
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = str(startup) + os.pathsep + env.get("PYTHONPATH", "")
    proc = subprocess.run(
        [sys.executable, str(ENTRYPOINT), "--data", str(dataset),
         "--output", str(output)],
        cwd=ROOT, env=env, capture_output=True, text=True,
        timeout=120, check=False,
    )
    assert proc.returncode == 0, proc.stdout + "\n" + proc.stderr
    metadata = json.loads((output / "run_metadata.json").read_text(encoding="utf-8"))
    assert metadata["train_rows"] == 80
    assert metadata["test_rows"] == 20
    assert metadata["rf_best_params"]["model__n_estimators"] == 10
    metrics = pd.read_csv(output / "model_metrics.csv", index_col=0)
    assert set(metrics.index) == {"logistic_regression", "random_forest_tuned"}
    features = data.drop(columns="target").iloc[:3]
    for name in metrics.index:
        model_file = output / f"{name}.joblib"
        assert model_file.stat().st_size > 0
        assert len(joblib.load(model_file).predict(features)) == 3
        assert (output / f"{name}_group_metrics_by_sex.csv").is_file()
        assert (output / f"{name}_confusion_matrix.png").stat().st_size > 0
        assert (output / f"{name}_roc.png").stat().st_size > 0
