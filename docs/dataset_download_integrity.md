# Dataset download integrity contract

This document describes the downloader implemented in `src/data.py` on the parent dataset-safety branch. It is a statement of **current code behavior**, not a certification of data quality, authenticity, or suitability for clinical use.

## Expected input

The downloader tries two public GitHub raw-file mirrors listed in `DATA_MIRRORS`, in order. It expects a CSV with **exactly 1,025 rows** and exactly these 14 column names (column order is not checked):

```text
age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal, target
```

The code checks CSV parseability, the presence of every expected column, the absence of extra columns, and row count. It does **not** check value ranges, numeric types, target encoding, missing values, duplicates, cryptographic checksums, or whether a mirror is an authoritative source. A syntactically valid but modified dataset can pass. The expected row count is specific to the coursework-compatible Kaggle-style derivative, not the 303-instance UCI Cleveland source.

## File replacement and failure behavior

1. Download one mirror into memory, with a 30-second request timeout.
2. Parse and validate the downloaded bytes **before** changing the destination.
3. Write validated bytes to a temporary file in the destination directory.
4. Use `os.replace` to replace the destination on the same filesystem; remove the temporary file in a `finally` block.
5. If a mirror fails, try the next one. If every mirror fails, raise `RuntimeError` with the collected errors.

A pre-existing destination is preserved when a mirror download, CSV parse, schema check, or row-count check fails. Atomic replacement avoids a partially written destination file in ordinary same-filesystem replacement scenarios. It does **not** guarantee durability across power loss, protect against malicious mirrors, or prevent a previously existing *valid* file from being replaced by a different CSV that passes the limited checks. The downloader does not check whether a destination already exists before downloading.

## Reproducibility and provenance limitations

The mirror URLs point to third-party, mutable branches, not pinned immutable dataset revisions. No expected SHA-256 digest or signed provenance manifest is enforced. Consequently, rerunning the downloader at a later date does **not** guarantee identical bytes or identical model results.

For a reproducible experiment, independently establish dataset licensing and provenance, preserve an authorized immutable copy, and record its SHA-256 hash, retrieval date, source URL/revision, preprocessing steps, environment, and random seeds. Do not treat the UCI background DOI in the repository README as proof that the mirrored 1,025-row CSV is byte-identical to the original UCI release.

## Offline verification

```bash
python -m pytest -q tests/test_download_dataset.py
python -m compileall -q src tests scripts
```

The regression tests mock network responses and check that invalid mirrors preserve existing data, fallback succeeds after an invalid first mirror, and a wrong row count is rejected. These tests do not download or authenticate the real dataset. They do not establish clinical validity. See `docs/ethics_and_limitations.md` for broader responsible-use limitations.
