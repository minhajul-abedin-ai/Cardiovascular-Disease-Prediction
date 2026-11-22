# Python 3.11 dependency reproducibility procedure

Status: **proposed validation procedure, not a validated lockfile**. Tracking: [issue #5](https://github.com/minhajul-abedin-ai/Cardiovascular-Disease-Prediction/issues/5).

## Evidence and provenance

[PR #8](https://github.com/minhajul-abedin-ai/Cardiovascular-Disease-Prediction/pull/8) produced a Python 3.11 dependency snapshot in [Actions run 43882630426](https://github.com/minhajul-abedin-ai/Cardiovascular-Disease-Prediction/actions/runs/43882630426), artifact ID `14232033331` (scheduled to expire 2026-11-30). GitHub Actions artifact metadata currently reports ZIP digest `sha256:6b564ff2cea275c6f8c1a2c77268f936bee80cb0e8db30fd3b3c217e5f9a374e` (checked 2026-11-21). Its `python311-ubuntu2404-freeze.txt` records 120 installed distributions on Ubuntu 24.04, Python 3.11.18. The snapshot's PR head SHA is `59a758e6b384f9c6bc2402bc362912448842979e`; the PR event/checkout SHA is `d16dae486d31335d5ffdb4ef18081434b11ae7a0`. These must not be conflated.

**Do not copy the snapshot into a production constraints file without validation.** A `pip freeze` snapshot may contain development tools, platform-specific packages, or packages not needed by the application. A constraints file limits versions but does not itself request installation.

## Snapshot preflight (before selecting constraints)

From the repository root, download artifact `14232033331` from the linked run and save it as `dependency-snapshot.zip`. The following **offline, standard-library-only** check prints the archive members, verifies the expected freeze entry exists, and rejects duplicate or non-exact package specifications. It does not prove that the pinned environment installs successfully. The regular expression rejects whitespace within version tokens; review any rejected freeze lines rather than weakening validation.

```bash
python - <<'PY'
from pathlib import Path
from zipfile import ZipFile
import hashlib
import re

archive = Path("dependency-snapshot.zip")
expected_sha256 = "6b564ff2cea275c6f8c1a2c77268f936bee80cb0e8db30fd3b3c217e5f9a374e"  # GitHub Actions artifact metadata, checked 2026-11-21
actual_sha256 = hashlib.sha256(archive.read_bytes()).hexdigest()
print("archive_sha256:", actual_sha256)
if actual_sha256 != expected_sha256:
    raise SystemExit("Artifact ZIP SHA-256 differs from GitHub Actions metadata; stop and investigate")
with ZipFile(archive) as z:
    names = z.namelist()
    print("members:", names)
    target = "python311-ubuntu2404-freeze.txt"
    if names.count(target) != 1:
        raise SystemExit(f"Expected exactly one {target} entry")
    lines = z.read(target).decode("utf-8").splitlines()
seen = set()
for line in lines:
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    match = re.fullmatch(r"([A-Za-z0-9][A-Za-z0-9._-]*)==([^\s;]+)", line)
    if not match:
        raise SystemExit(f"Review non-exact freeze entry: {line}")
    name = re.sub(r"[-_.]+", "-", match.group(1)).lower()
    if name in seen:
        raise SystemExit(f"Duplicate distribution: {name}")
    seen.add(name)
print("unique_exact_pins:", len(seen))
PY
```

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

The SHA-256-verified artifact `14232033331` was downloaded and its freeze member compared with the nine direct entries in the **main-branch** `requirements.txt` (blob `9624a0ee4ae77cdcab6e4fe672f82cc11fb7e0b5`). Every direct distribution appears exactly once in the snapshot. These are observed versions, **not** proposed or tested constraints.

| Direct requirement | Captured installed version |
| --- | --- |
| `pandas>=2.0` | `3.1.1` |
| `numpy>=1.24` | `2.4.6` |
| `matplotlib>=3.7` | `3.11.2` |
| `seaborn>=0.12` | `0.13.2` |
| `scikit-learn>=1.3` | `1.9.1` |
| `imbalanced-learn>=0.11` | `0.14.2` |
| `joblib>=1.3` | `1.6.0` |
| `jupyter>=1.0` | `1.1.1` |
| `pytest>=7.4` | `9.2.0` |

The artifact contains 120 exact package pins in total, including transitive and development dependencies. All nine observed versions meet their stated lower bounds when interpreted using standard Python packaging version ordering. The artifact's original workflow succeeded, but **this audit did not run a fresh resolver, install, `pip check`, or repository tests**. In particular, the presence of a distribution in `pip freeze` does not establish that a clean install using a constraints candidate will succeed. Next: review the full transitive set, produce a minimal constraints candidate, and validate in a clean Python 3.11/Ubuntu 24.04 environment before enforcing it in CI.
