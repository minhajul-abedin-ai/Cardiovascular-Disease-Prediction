# Results reported in the submitted code PDF

These values are transcribed from the output shown in the assignment code export; they are not newly rerun results from this repository.

## Data audit

- Initial dataset: **1,025 rows × 14 columns**
- Exact duplicates detected: **723**
- Unique rows after deduplication: **302**
- Missing values shown in the original dataframe summary: **0**

## Descriptive sex distribution after deduplication

- Male: **206**
- Female: **96**
- Ratio: **2.15 : 1**
- Observed disease prevalence in the coursework output:
  - Female: **75.00%**
  - Male: **44.66%**

These prevalence values are descriptive characteristics of the dataset and should not be interpreted as causal or population-level clinical estimates.

## Logistic Regression

- 5-fold CV mean recall: **87.81% ± 7.80%**
- Test confusion matrix: **TN=23, FP=5, FN=6, TP=27**
- Accuracy: **81.97%**
- Precision: **84.38%**
- Recall: **81.82%**
- F1: **83.08%**
- ROC-AUC: **88.20%**

## Tuned Random Forest

Best parameters reported:

- `max_depth = 15`
- `min_samples_leaf = 1`
- `min_samples_split = 2`
- `n_estimators = 200`

Test metrics:

- Accuracy: **75.41%**
- Precision: **76.47%**
- Recall: **78.79%**
- F1: **77.61%**
- ROC-AUC: **86.53%**

## Important correction

The final sentence in the code export says Random Forest improved accuracy and precision, but the displayed table shows Logistic Regression was higher on every reported test metric. This repository uses the numeric table rather than the contradictory sentence.
