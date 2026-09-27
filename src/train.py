from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler

from data import IQRClipper, audit_and_deduplicate, load_raw_data
from evaluation import (
    classification_metrics,
    group_metrics_by_sex,
    save_confusion_matrix,
    save_roc_pr_curves,
)

RANDOM_STATE = 42


def build_logistic_pipeline() -> Pipeline:
    return Pipeline(
        steps=[
            ("iqr", IQRClipper()),
            ("scaler", StandardScaler()),
            ("smote", SMOTE(random_state=RANDOM_STATE)),
            ("model", LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)),
        ]
    )


def build_rf_pipeline() -> Pipeline:
    return Pipeline(
        steps=[
            ("iqr", IQRClipper()),
            ("smote", SMOTE(random_state=RANDOM_STATE)),
            ("model", RandomForestClassifier(random_state=RANDOM_STATE)),
        ]
    )


def run(data_path: Path, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    raw = load_raw_data(data_path)
    df, audit = audit_and_deduplicate(raw)

    X = df.drop(columns="target")
    y = df["target"]
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    logistic = build_logistic_pipeline()
    logistic_cv_recall = cross_val_score(logistic, X_train, y_train, cv=cv, scoring="recall")
    logistic.fit(X_train, y_train)

    rf = build_rf_pipeline()
    param_grid = {
        "model__n_estimators": [50, 100, 200],
        "model__max_depth": [5, 10, 15, None],
        "model__min_samples_split": [2, 5, 10],
        "model__min_samples_leaf": [1, 2, 4],
    }
    grid = GridSearchCV(
        estimator=rf,
        param_grid=param_grid,
        cv=cv,
        scoring="recall",
        n_jobs=-1,
        verbose=1,
    )
    grid.fit(X_train, y_train)
    tuned_rf = grid.best_estimator_

    models = {
        "logistic_regression": logistic,
        "random_forest_tuned": tuned_rf,
    }

    results = {}
    for name, model in models.items():
        pred = model.predict(X_test)
        prob = model.predict_proba(X_test)[:, 1]
        results[name] = classification_metrics(y_test, pred, prob)
        fairness = group_metrics_by_sex(y_test.to_numpy(), pred, X_test["sex"].to_numpy())
        fairness.to_csv(output_dir / f"{name}_group_metrics_by_sex.csv", index=False)
        save_confusion_matrix(y_test, pred, name.replace("_", " ").title(), output_dir / f"{name}_confusion_matrix.png")
        save_roc_pr_curves(y_test, prob, name.replace("_", " ").title(), output_dir / f"{name}_roc.png")
        joblib.dump(model, output_dir / f"{name}.joblib")

    results_table = pd.DataFrame(results).T
    results_table.to_csv(output_dir / "model_metrics.csv")

    metadata = {
        "data_audit": audit.__dict__,
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "logistic_cv_recall_mean": float(logistic_cv_recall.mean()),
        "logistic_cv_recall_std": float(logistic_cv_recall.std()),
        "rf_best_params": grid.best_params_,
        "note": "SMOTE is used for target-class imbalance only; demographic fairness is audited separately.",
    }
    (output_dir / "run_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print("\nData audit:", audit)
    print("\nModel metrics:\n", results_table)
    print("\nBest Random Forest parameters:", grid.best_params_)
    return {"metrics": results, "metadata": metadata}


def main() -> None:
    parser = argparse.ArgumentParser(description="Train heart-disease prediction models")
    parser.add_argument("--data", default="data/heart_data.csv")
    parser.add_argument("--output", default="results/reproduced")
    args = parser.parse_args()
    run(Path(args.data), Path(args.output))


if __name__ == "__main__":
    main()
