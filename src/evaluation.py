from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    auc,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_curve,
)


def classification_metrics(y_true, y_pred, y_prob) -> dict[str, float]:
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    precision_curve, recall_curve, _ = precision_recall_curve(y_true, y_prob)
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "roc_auc": auc(fpr, tpr),
        "pr_auc": auc(recall_curve, precision_curve),
    }


def group_metrics_by_sex(y_true, y_pred, sex) -> pd.DataFrame:
    """Descriptive group metrics; not a claim that a model is 'fair'."""
    frame = pd.DataFrame({"y_true": y_true, "y_pred": y_pred, "sex": sex}).reset_index(drop=True)
    rows = []
    for group, g in frame.groupby("sex"):
        tn, fp, fn, tp = confusion_matrix(g.y_true, g.y_pred, labels=[0, 1]).ravel()
        rows.append(
            {
                "sex": int(group),
                "n": len(g),
                "observed_positive_rate": float(g.y_true.mean()),
                "predicted_positive_rate": float(g.y_pred.mean()),
                "tpr_recall": tp / (tp + fn) if (tp + fn) else np.nan,
                "fpr": fp / (fp + tn) if (fp + tn) else np.nan,
                "precision": tp / (tp + fp) if (tp + fp) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def save_confusion_matrix(y_true, y_pred, title: str, out_path: str | Path) -> None:
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(5, 4))
    image = ax.imshow(cm)
    fig.colorbar(image, ax=ax)
    for (i, j), value in np.ndenumerate(cm):
        ax.text(j, i, str(value), ha="center", va="center")
    ax.set_title(title)
    ax.set_xlabel("Predicted label")
    ax.set_ylabel("True label")
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def save_roc_pr_curves(y_true, y_prob, model_name: str, out_path: str | Path) -> None:
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    precision, recall, _ = precision_recall_curve(y_true, y_prob)

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(fpr, tpr, label=f"ROC AUC = {auc(fpr, tpr):.3f}")
    ax.plot([0, 1], [0, 1], linestyle="--")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title(f"{model_name} — ROC Curve")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)

    pr_out = Path(out_path).with_name(Path(out_path).stem.replace("roc", "pr") + ".png")
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(recall, precision, label=f"PR AUC = {auc(recall, precision):.3f}")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title(f"{model_name} — Precision-Recall Curve")
    ax.legend()
    fig.tight_layout()
    fig.savefig(pr_out, dpi=180)
    plt.close(fig)
