# Python 3.11 dependency reproducibility procedure

Status: **proposed validation procedure, not a validated lockfile**. Tracking: [issue #5](https://github.com/minhajul-abedin-ai/Cardiovascular-Disease-Prediction/issues/5).

## Evidence and provenance

[PR #8](https://github.com/minhajul-abedin-ai/Cardiovascular-Disease-Prediction/pull/8) produced a Python 3.11 dependency snapshot in [Actions run 43882630426](https://github.com/minhajul-abedin-ai/Cardiovascular-Disease-Prediction/actions/runs/43882630426), artifact ID `14232033331` (scheduled to expire 2026-11-30). GitHub Actions artifact metadata currently reports ZIP digest `sha256:6b564ff2cea275c6f8c1a2c77268f936bee80cb0e8db30fd3b3c217e5f9a374e` (checked 2026-11-21). Its `python311-ubuntu2404-freeze.txt` records 120 installed distributions on Ubuntu 24.04, Python 3.11.18. The snapshot's PR head SHA is `59a758e6b384f9c6bc2402bc362912448842979e`; the PR event/checkout SHA is `d16dae486d31335d5ffdb4ef18081434b11ae7a0`. These must not be conflated.

**Do not copy the snapshot into a production constraints file without validation.** A `pip freeze` snapshot may contain development tools, platform-specific packages, or packages not needed by the application. A constraints file limits versions but does not itself request installation.

## Snapshot preflight (before selecting constraints)

From the repository root, download artifact `14232033331` from the linked run and save it as `dependency-snapshot.zip`. Install the repository's declared `packaging` dependency first if needed. Run the **committed validator**, rather than copying an older inline regular expression that can accept malformed package names or invalid PEP 440 versions:

```bash
python -m pip install 'packaging>=24.0'
python scripts/validate_dependency_snapshot.py dependency-snapshot.zip \
  --sha256 6b564ff2cea275c6f8c1a2c77268f936bee80cb0e8db30fd3b3c217e5f9a374e \
  --member python311-ubuntu2404-freeze.txt
```

This offline validation checks the ZIP SHA-256 against the recorded GitHub metadata, ZIP CRC, a single expected member, exact pins, normalized duplicate names, valid package-name boundaries and PEP 440 versions. It requires the `packaging` library but does **not** install or resolve the snapshot's dependencies, establish a lockfile, or prove a clean Python 3.11 installation.

Review any rejected entries manually rather than silently deleting them. Check the recorded PR head and checkout/event SHAs separately before using the snapshot. The expected ZIP hash is from GitHub Actions artifact metadata, not an independently signed or immutable release. Recheck artifact ID and digest against GitHub before use; this comparison detects mismatched downloads but does not independently authenticate GitHub.

## Candidate generation and clean validation

1. Download the named artifact from the linked Actions run before expiration. Extract the freeze file and inspect every package/version, especially the Jupyter stack and build tools. Store a reviewed candidate as `constraints/python311-ubuntu2404.txt` on a separate PR branch. Do not edit the current default branch directly.
2. On a fresh Ubuntu 24.04 / Python 3.11 virtual environment, run the following from the repository root (after reviewing the candidate):

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -c constraints/python311-ubuntu2404.txt
python -m pip check
python -m pytest -q
python -m compileall -q src tests scripts
python -m pip freeze > validated-freeze.txt
```

3. Record the exact Python/pip versions, runner OS, candidate SHA-256, test count, job URL and any resolver warnings. Compare the resulting freeze against the reviewed candidate; investigate discrepancies rather than silently claiming bit-for-bit reproducibility.
4. Add `-c constraints/python311-ubuntu2404.txt` to CI's dependency install only after the clean run succeeds. Prefer an explicit Ubuntu runner image over `ubuntu-latest` when recording OS-specific reproducibility evidence. Keep tests offline; do not download or commit medical datasets.
5. Document a deliberate dependency update process: regenerate on the stated Python/OS, review the diff and licenses, run the same clean checks, and update the pinned file and CI together.

## Scope of the claim

Passing the checks demonstrates dependency compatibility and the repository's offline tests for the tested environment. It **does not** reproduce the coursework's numerical metrics, guarantee cross-platform installs, prove clinical safety, or validate a dataset that was not used. Keep the educational/non-clinical disclaimer intact.

## Direct requirement audit against the captured snapshot (2026-11-22)

GitHub Actions artifact `14232033331` was downloaded again on 2026-11-22. Its computed ZIP SHA-256 was `6b564ff2cea275c6f8c1a2c77268f936bee80cb0e8db30fd3b3c217e5f9a374e`, matching the recorded artifact digest. The `python311-ubuntu2404-freeze.txt` member contains 120 exact distribution pins.

All **ten current PR-branch** direct requirements (requirements.txt blob `ad015a9f2101e118d40da47c798aa33874ad2a80`) were compared against the freeze member using canonicalized package names and `packaging.requirements.Requirement` / `packaging.version.Version`. Each distribution was present, and each captured version satisfies its declared lower bound. This extends the earlier nine-package audit to include `packaging>=24.0`.

| Direct requirement | Captured version | Minimum satisfied? |
| --- | --- | --- |
| `pandas>=2.0` | `3.1.1` | Yes |
| `numpy>=1.24` | `2.4.6` | Yes |
| `matplotlib>=3.7` | `3.11.2` | Yes |
| `seaborn>=0.12` | `0.13.2` | Yes |
| `scikit-learn>=1.3` | `1.9.1` | Yes |
| `imbalanced-learn>=0.11` | `0.14.2` | Yes |
| `joblib>=1.3` | `1.6.0` | Yes |
| `jupyter>=1.0` | `1.1.1` | Yes |
| `pytest>=7.4` | `9.2.0` | Yes |
| `packaging>=24.0` | `26.3` | Yes |

**Limitations:** This is an offline audit of a previously installed environment, **not** a fresh resolver run, clean Python 3.11 installation, `pip check`, or repository test execution. The captured versions are observations, not tested constraints. Next: review transitive pins and build a minimal constraints candidate, then validate in a clean Python 3.11/Ubuntu 24.04 environment before CI enforcement.
