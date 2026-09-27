# Source-code reconstruction notes

This repository was reconstructed from the submitted COM747 code PDF and report. The original PDF contains executable Python cells for:

- loading a 1,025-row heart-disease dataset;
- duplicate detection/removal;
- IQR clipping for `trestbps`, `chol` and `thalach`;
- correlation analysis and a gender-prevalence check;
- train/test splitting;
- SMOTE;
- StandardScaler;
- Logistic Regression with 5-fold stratified cross-validation;
- Random Forest tuning with GridSearchCV;
- ROC, precision-recall and confusion-matrix evaluation;
- Random Forest Gini feature importance.

The PDF is therefore a **code export / code evidence document**, not only a written report.

## Corrections made in the portfolio version

The repository contains two implementations:

1. `src/legacy_assignment_reconstruction.py` — a readable reconstruction that stays close to the submitted sequence.
2. `src/train.py` — the recommended leakage-aware version for a public portfolio.

The improved version makes several methodological corrections:

### 1. IQR thresholds are fitted only on training folds

In the submitted code, IQR clipping happens before the train/test split. That lets information from the eventual test data influence preprocessing thresholds. The portfolio implementation wraps IQR clipping in a scikit-learn transformer so bounds are learned only from training data inside CV.

### 2. SMOTE is used for target-class imbalance, not demographic fairness

The submitted notebook describes SMOTE as resolving gender bias. Standard SMOTE balances the **target class**, not gender groups. The portfolio implementation uses SMOTE only for class imbalance and reports sex-group metrics separately.

### 3. SMOTE is inside the cross-validation pipeline

The submitted code performs SMOTE before cross-validation. Synthetic neighbours may therefore be shared across folds. The portfolio pipeline applies SMOTE within each training fold using `imblearn.pipeline.Pipeline`.

### 4. Final model interpretation follows the reported numbers

The submitted output reports:

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 81.97% | 84.38% | 81.82% | 83.08% | 88.20% |
| Tuned Random Forest | 75.41% | 76.47% | 78.79% | 77.61% | 86.53% |

A sentence in the code PDF says the Random Forest improved accuracy and precision, but the table shows the opposite. This repository treats the numerical table as authoritative and does not repeat that contradictory claim.
