# Experimental Python 3.11 dependency snapshot

This directory contains **experimental** constraints, not a supported lockfile.
The transitive snapshot was copied from `pip freeze` in [CI run
45057730574](https://github.com/minhajul-abedin-ai/Cardiovascular-Disease-Prediction/actions/runs/45057730574).
It contains 118 installed distributions, including notebook and test tooling;
this is a resolved *environment inventory*, not proof that every distribution
is required by the project.

## What has been verified

The separate [snapshot validation workflow](../.github/workflows/validate-transitive-snapshot.yml)
installs `requirements.txt` with the full snapshot as pip constraints on
Ubuntu 24.04 / Python 3.11, runs `pip check`, offline pytest and compilation,
then compares `pip freeze` to the snapshot. [CI run
45074674767](https://github.com/minhajul-abedin-ai/Cardiovascular-Disease-Prediction/actions/runs/45074674767)
passed those checks (28 tests). This is evidence for **one runner platform
and time**, not for macOS, Windows, other Python versions or future package
index availability.

## Reproduce the validation locally

Use a **fresh** Python 3.11 virtual environment on Ubuntu 24.04; do not install
into a shared or system Python environment.

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt -c constraints/python311-transitive-snapshot.txt
python -m pip check
python -m pytest -q
python -m compileall -q src tests scripts
grep -v '^#' constraints/python311-transitive-snapshot.txt | grep -v '^$' | sort -f > /tmp/cvd-expected.txt
python -m pip freeze | sort -f > /tmp/cvd-actual.txt
diff -u /tmp/cvd-expected.txt /tmp/cvd-actual.txt
```

The version comparison requires a clean environment; preinstalled packages
can cause extra lines. A successful comparison proves only equality of
reported package names and versions. Constraints do **not** force pip to
install every listed package.

## Limits and next experiment

* The file does not include wheel/sdist SHA-256 hashes, so it does not provide
  artifact-level integrity or protection from package replacement.
* It is not a cross-platform lock: binary wheels, markers, build dependencies,
  and resolver behavior can vary.
* A `pip freeze` inventory can include packages not needed by runtime or tests.
* Do not replace the default install path or enforce the snapshot in production
  without review.

Next, use a fresh environment and dependency graph (for example
`pip inspect` and `pipdeptree`) to distinguish the required dependency
closure from incidental packages. Verify any smaller candidate with a second
clean installation, `pip check`, the complete offline test suite, and a
version comparison. Only then consider generating a platform-specific,
hash-verified requirements file with an appropriate locking tool. Never
invent hashes from version numbers; hashes must come from verified artifacts.
