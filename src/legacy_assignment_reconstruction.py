"""Clean reconstruction of the code visible in the submitted COM747 PDF.

This file intentionally mirrors the original assignment sequence closely.
For a leakage-aware portfolio implementation, use src/train.py instead.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    auc,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_curve,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler

RANDOM_STATE = 42
DATA_PATH = Path("data/heart_data.csv")


def main() -> None:
    sns.set_theme(style="whitegrid", palette="muted")
    df = pd.read_csv(DATA_PATH)
    print(f"Initial dataset shape: {df.shape}")

    duplicates = int(df.duplicated().sum())
    print(f"Exact duplicate rows: {duplicates}")
    df = df.drop_duplicates().reset_index(drop=True)

    continuous_features = ["trestbps", "chol", "thalach"]
    for col in continuous_features:
        q1, q3 = df[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        df[col] = df[col].clip(q1 - 1.5 * iqr, q3 + 1.5 * iqr)

    corr = df.corr(numeric_only=True)
    mask = np.triu(np.ones_like(corr, dtype=bool))
    plt.figure(figsize=(12, 8))
    sns.heatmap(corr, mask=mask, annot=True, cmap="RdYlBu_r", fmt=".2f")
    plt.title("Advanced Feature Correlation Matrix")
    plt.tight_layout()
    plt.show()

    disease_by_gender = df.groupby("sex")["target"].mean() * 100
    print("\nObserved disease prevalence by sex (%):")
    print(disease_by_gender)

    X = df.drop(columns="target")
    y = df["target"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    smote = SMOTE(random_state=RANDOM_STATE)
    X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_balanced)
    X_test_scaled = scaler.transform(X_test)

    log_model = LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    scores = cross_val_score(log_model, X_train_scaled, y_train_balanced, cv=cv, scoring="recall")
    print(f"\nLogistic Regression 5-fold recall: {scores.mean():.4f} +/- {scores.std():.4f}")
    log_model.fit(X_train_scaled, y_train_balanced)
    log_preds = log_model.predict(X_test_scaled)
    log_probs = log_model.predict_proba(X_test_scaled)[:, 1]
    print("\nLogistic Regression report:\n", classification_report(y_test, log_preds))

    grid = {
        "n_estimators": [50, 100, 200],
        "max_depth": [5, 10, 15, None],
        "min_samples_split": [2, 5, 10],
        "min_samples_leaf": [1, 2, 4],
    }
    search = GridSearchCV(
        RandomForestClassifier(random_state=RANDOM_STATE),
        grid,
        cv=5,
        scoring="recall",
        n_jobs=-1,
        verbose=1,
    )
    search.fit(X_train_scaled, y_train_balanced)
    rf = search.best_estimator_
    rf_preds = rf.predict(X_test_scaled)
    rf_probs = rf.predict_proba(X_test_scaled)[:, 1]

    log_auc = auc(*roc_curve(y_test, log_probs)[:2])
    rf_auc = auc(*roc_curve(y_test, rf_probs)[:2])
    results = pd.DataFrame(
        {
            "Model": ["Logistic Regression (Baseline)", "Random Forest (Tuned)"],
            "Accuracy": [accuracy_score(y_test, log_preds), accuracy_score(y_test, rf_preds)],
            "Precision": [precision_score(y_test, log_preds), precision_score(y_test, rf_preds)],
            "Recall": [recall_score(y_test, log_preds), recall_score(y_test, rf_preds)],
            "F1": [f1_score(y_test, log_preds), f1_score(y_test, rf_preds)],
            "ROC-AUC": [log_auc, rf_auc],
        }
    )
    print("\nFinal comparison:\n", results)
    better = results.loc[results["ROC-AUC"].idxmax(), "Model"]
    print(f"\nBased on test ROC-AUC in this reconstruction, the stronger model is: {better}")


if __name__ == "__main__":
    main()
