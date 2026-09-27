# Ethics, fairness and limitations

This is an educational machine-learning project, not a clinical decision-support product.

## Clinical limitation

The model is trained on a small public benchmark dataset. It should not be used to diagnose, screen or treat any person. Real clinical deployment would require prospective validation, representative multi-site data, calibration, monitoring, governance and qualified medical oversight.

## Fairness limitation

The coursework observed different disease prevalence by recorded sex and a 2.15:1 male/female sample ratio after deduplication. Those observations do not by themselves prove algorithmic discrimination.

SMOTE balances outcome classes; it does not guarantee demographic fairness. The portfolio implementation therefore reports group-wise predicted-positive rate, recall/TPR, FPR and precision by sex as descriptive diagnostics.

## Data limitation

The popular 1,025-row Kaggle version contains many duplicated records. The coursework correctly detected 723 exact duplicates and removed them before modelling. This repository keeps that step and also moves preprocessing into train-fitted pipelines to reduce leakage risk.

## Explainability limitation

Random Forest Gini feature importance is a global importance measure. It does not establish causality and may be biased toward features with more possible split points. For a stronger XAI extension, permutation importance or SHAP could be added.
