"""Offline regression tests for safe dataset downloads."""
from io import BytesIO
import sys
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import data


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self.payload


def valid_csv():
    row = {name: 0 for name in data.EXPECTED_COLUMNS}
    return pd.DataFrame([row] * 1025).to_csv(index=False).encode()


def test_failed_mirrors_preserve_existing_dataset(tmp_path):
    destination = tmp_path / "heart.csv"
    destination.write_bytes(b"existing verified data")
    with patch.object(data, "DATA_MIRRORS", ["bad"]), patch.object(
        data, "urlopen", return_value=FakeResponse(b"not a valid csv")
    ):
        with pytest.raises(RuntimeError, match="Could not download"):
            data.download_dataset(destination)
    assert destination.read_bytes() == b"existing verified data"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["heart.csv"]


def test_invalid_first_mirror_then_valid_second(tmp_path):
    destination = tmp_path / "heart.csv"
    payload = valid_csv()
    responses = [FakeResponse(b"broken"), FakeResponse(payload)]
    with patch.object(data, "DATA_MIRRORS", ["bad", "good"]), patch.object(
        data, "urlopen", side_effect=responses
    ):
        assert data.download_dataset(destination) == destination
    assert destination.read_bytes() == payload
    assert sorted(p.name for p in tmp_path.iterdir()) == ["heart.csv"]


def test_wrong_row_count_does_not_replace_existing_file(tmp_path):
    destination = tmp_path / "heart.csv"
    destination.write_bytes(b"keep me")
    payload = pd.DataFrame([{name: 0 for name in data.EXPECTED_COLUMNS}]).to_csv(index=False).encode()
    with patch.object(data, "DATA_MIRRORS", ["wrong-size"]), patch.object(
        data, "urlopen", return_value=FakeResponse(payload)
    ):
        with pytest.raises(RuntimeError, match="Expected 1025 rows"):
            data.download_dataset(destination)
    assert destination.read_bytes() == b"keep me"
