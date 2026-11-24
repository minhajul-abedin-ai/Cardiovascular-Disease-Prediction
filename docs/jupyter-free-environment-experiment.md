# Jupyter-free dependency experiment (draft PR #20)

This document describes an **experimental** dependency set, not a replacement for the repository's default environment.

## Install by use case

- **Existing documented workflow and interactive notebooks:** `python -m pip install -r requirements.txt`. This retains the `jupyter` metapackage.
- **Command-line pipeline and automated tests (experimental):** `python -m pip install -r requirements-no-jupyter-experiment.txt`. This intentionally omits the `jupyter` metapackage. It does **not** install or promise a Jupyter notebook server, JupyterLab, or an interactive kernel.

Use a fresh Python 3.11 virtual environment for each comparison; do not install both requirements files into the same environment and infer package savings.

## Evidence and boundaries

At commit `2b753e7`, [comparison run 45188162002](https://github.com/minhajul-abedin-ai/Cardiovascular-Disease-Prediction/actions/runs/45188162002) reported **120 installed distributions** for the default requirements and **27** for the experimental requirements (93 fewer, or 77.5%, in those clean runners). Both environments passed `pip check`, four discovered offline pytest tests, and source compilation. These are environment-specific counts, not a universal size or speed benchmark.

Subsequent workflow changes added notebook JSON/code-cell syntax validation, execution of the notebook setup cell, and a synthetic 80-row Logistic Regression fit/predict smoke test. [Comparison run 45254069078](https://github.com/minhajul-abedin-ai/Cardiovascular-Disease-Prediction/actions/runs/45254069078) succeeded for both matrix environments at commit `319ef27`. The synthetic records are test fixtures, **not clinical data** and not evidence of predictive performance.

At commit `2e17bf1`, [comparison run 45283679861](https://github.com/minhajul-abedin-ai/Cardiovascular-Disease-Prediction/actions/runs/45283679861) completed successfully in **both** requirements matrix jobs. GitHub Actions marks the `Run offline tests` step successful in each, along with dependency checks, source compilation, notebook syntax validation, notebook setup-cell execution, and synthetic-data computation. The separate [ML pipeline run 45283679872](https://github.com/minhajul-abedin-ai/Cardiovascular-Disease-Prediction/actions/runs/45283679872) also succeeded, including its offline unit-test step. The added `tests/test_dataset_interface_offline.py` uses controlled fixtures/mocks for local CSV loading, required-column validation, fallback to a second mirror, and invalid-data cleanup. **The job summaries confirm successful test steps, but do not independently expose individual test-case names/counts or prove real network/dataset availability.**

**Not verified:** launching an interactive Jupyter server/kernel; executing every notebook cell in order; downloading and validating the real dataset; full training/tuning on the real dataset; reproducibility of the original coursework metrics; or clinical suitability. The notebook setup and synthetic computation smoke tests must not be described as full notebook execution.

## Current test evidence and CLI dependency boundary

At commit `b0a19c8`, [comparison run 45315556158](https://github.com/minhajul-abedin-ai/Cardiovascular-Disease-Prediction/actions/runs/45315556158) passed **8 pytest tests in each of the two matrix environments**, with individual test names visible via `pytest -vv`. The separate [ML pipeline run 45315556176](https://github.com/minhajul-abedin-ai/Cardiovascular-Disease-Prediction/actions/runs/45315556176) passed 8 tests. These are **24 test executions across three jobs**, not 24 distinct tests. This supersedes the earlier uncertainty about test counts, but does not validate live data downloads or full model training.

Static import inspection of `src/train.py` and `src/data.py` confirms that the command-line training path uses pandas, NumPy, scikit-learn, imbalanced-learn, joblib, and plotting utilities, without importing the `jupyter` metapackage. The experimental requirements retain the baseline package declarations other than `jupyter>=1.0`. The successful synthetic fit/predict smoke test is consistent with this dependency boundary; it does **not** prove that the complete `GridSearchCV` training and artifact-writing path works on the real dataset. The repository's default README quick start still installs `requirements.txt`, so interactive notebook users retain the baseline environment. No default requirements or lock snapshots were changed.

## Latest verified offline integration evidence (commit `e6b9b20`)

At commit `e6b9b20`, [dependency comparison run 45388230679](https://github.com/minhajul-abedin-ai/Cardiovascular-Disease-Prediction/actions/runs/45388230679) reported **13 pytest tests passed** in the standard environment and **13 passed** in the Jupyter-free environment. The separate [ML pipeline run 45388230689](https://github.com/minhajul-abedin-ai/Cardiovascular-Disease-Prediction/actions/runs/45388230689) reported **13 passed**. These are **39 executions of 13 tests across three jobs**, not 39 unique tests. The successful subprocess CLI smoke test (`test_cli_trains_and_writes_reloadable_models`) uses synthetic fixtures and a reduced search to check command-line training and reloadable model artifacts. Earlier offline tests cover training artifacts through the Python entry point, CLI help, unknown arguments, and missing-dataset failures.

This evidence supersedes the older 8-test status above. It does **not** establish real-dataset model performance, a complete production-scale hyperparameter search, end-to-end interactive notebook execution, or clinical suitability. Keep the Jupyter-free requirements experimental and the PR in draft until separately reviewed.

## Reproduce the checks

From a fresh Python 3.11 environment, choose one requirements file and run:

```bash
python -m pip install -r requirements-no-jupyter-experiment.txt
python -m pip check
python -m pytest -vv
python -m compileall -q src tests scripts
```

For the baseline, replace the requirements filename with `requirements.txt`. The notebook-specific checks live in `.github/workflows/compare-no-jupyter.yml` and run on GitHub Actions. The commands above do not execute the notebook or download the dataset.

## Documentation-only CI trigger check

The experimental comparison workflow includes `docs/**` in its pull-request path filter as of commit `3c36e14`. This documentation-only update is intended to exercise that filter. A successful run associated with this commit would demonstrate that the workflow can start for a documentation-only change on this PR; it would **not** establish that every possible documentation change triggers every repository workflow. Inspect the commit-associated workflow run and job conclusions before recording the trigger as verified.

## Before proposing a default change

Validate the real-data loading interface with controlled fixtures, document any separate interactive-notebook dependencies, and review the complete CI results. Keep PR #20 draft and do not change `requirements.txt` or the pinned snapshots solely on the strength of the smoke tests.
