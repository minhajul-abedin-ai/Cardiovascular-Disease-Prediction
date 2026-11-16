# Dependency reproducibility (Python 3.11)

This project currently declares **minimum** dependency versions in `requirements.txt`. It does **not** ship a tested lockfile. Consequently, two installs at different times may resolve different direct or transitive packages. A successful CI run does not prove that the original coursework metrics can be reproduced.

## Record an environment for an experiment

Use a clean Python 3.11 environment (the version used by GitHub Actions). On Linux/macOS:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip freeze --all > environment-resolved.txt
python -m pytest -q
python -m compileall -q src tests scripts
python --version
```

Keep `environment-resolved.txt` with the experiment's logs or artifact bundle, alongside the commit SHA, OS/architecture, Python version, installation date and dataset source/checksum. **Do not commit this local snapshot as a project-wide tested lockfile**: it reflects only the environment where it was generated. `pip freeze` records installed versions, but not artifact hashes or a cross-platform resolution guarantee.

To attempt to recreate that *same-platform* environment later, start with another clean Python 3.11 environment and install the captured snapshot:

```bash
python -m pip install -r environment-resolved.txt
python -m pip check
python -m pytest -q
python -m compileall -q src tests scripts
```

The commands above are instructions, **not claimed verification results**. Dataset downloads and full model training are deliberately excluded from offline unit-test verification. Even with matching packages, differences in dataset content, platform and randomness can affect numerical results.

## Follow-up needed before calling CI reproducible

Track [issue #5](https://github.com/minhajul-abedin-ai/Cardiovascular-Disease-Prediction/issues/5): generate and review an exact, transitive Python 3.11 dependency lock/constraints artifact; validate installation and tests in a clean environment; then configure CI to consume it. Record the actual test run and package versions before claiming a tested lock. This document does **not** close that issue.
