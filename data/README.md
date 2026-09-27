# Dataset

The original coursework code expects a file named `heart_data.csv` with **1,025 rows and 14 columns**:

`age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal, target`

The submitted coursework output reports **723 exact duplicate rows**, leaving **302 unique rows** after deduplication.

## Get the data

Run:

```bash
python scripts/download_dataset.py
```

The script downloads the same widely used 1,025-row Kaggle/UCI-derived `heart.csv` format from a public mirror and saves it as `data/heart_data.csv`.

## Provenance

The 1,025-row file is commonly distributed as the **Heart Disease Dataset** on Kaggle (`johnsmith88/heart-disease-dataset`) and is derived from the UCI Heart Disease data. The UCI Heart Disease dataset is credited to Andras Janosi, William Steinbrunn, Matthias Pfisterer and Robert Detrano.

This repository does **not** claim ownership of the dataset. The download script keeps raw-data provenance separate from the project code.

## Important note

The raw UCI Cleveland database contains 303 instances. The 1,025-row Kaggle-formatted version used in the assignment contains repeated records and different coding conventions. Results from other Cleveland variants may not exactly reproduce the assignment metrics.
