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

## Reproduce the checks

From a fresh Python 3.11 environment, choose one requirements file and run:

```bash
python -m pip install -r requirements-no-jupyter-experiment.txt
python -m pip check
python -m pytest -q
python -m compileall -q src tests scripts
```

For the baseline, replace the requirements filename with `requirements.txt`. The notebook-specific checks live in `.github/workflows/compare-no-jupyter.yml` and run on GitHub Actions. The commands above do not execute the notebook or download the dataset.

## Before proposing a default change

Validate the real-data loading interface with controlled fixtures, document any separate interactive-notebook dependencies, and review the complete CI results. Keep PR #20 draft and do not change `requirements.txt` or the pinned snapshots solely on the strength of the smoke tests.
