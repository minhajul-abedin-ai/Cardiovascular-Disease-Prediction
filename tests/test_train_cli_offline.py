"""Subprocess CLI contract checks requiring no network or clinical dataset.

The full training run is covered separately by test_training_artifacts_offline.py.
These checks exercise the actual Python entry point and argparse error paths.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRYPOINT = ROOT / "src" / "train.py"


def invoke(*args):
    return subprocess.run(
        [sys.executable, str(ENTRYPOINT), *map(str, args)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def test_cli_help_documents_data_and_output_flags():
    result = invoke("--help")
    assert result.returncode == 0, result.stderr
    assert "--data" in result.stdout
    assert "--output" in result.stdout


def test_cli_rejects_unknown_flag_without_creating_outputs(tmp_path):
    output = tmp_path / "artifacts"
    result = invoke("--unknown-option", "--output", output)
    assert result.returncode == 2
    assert "unrecognized arguments" in result.stderr
    assert not output.exists()


def test_cli_missing_dataset_fails_without_training_artifacts(tmp_path):
    missing = tmp_path / "does-not-exist.csv"
    output = tmp_path / "artifacts"
    result = invoke("--data", missing, "--output", output)
    assert result.returncode != 0
    assert "Dataset not found" in result.stderr
    assert not output.exists() or not list(output.glob("*.joblib"))
