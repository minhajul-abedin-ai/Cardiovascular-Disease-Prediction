"""Offline contract tests for the real CSV loading and mirror fallback interface.

All rows are synthetic. No network requests or clinical claims are involved.
"""
import sys
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import data
from data import EXPECTED_COLUMNS, download_dataset, load_raw_data


def synthetic_csv(rows=1025, *, drop_column=None):
    columns = [column for column in EXPECTED_COLUMNS if column != drop_column]
    records = []
    for i in range(rows):
        record = {name: i % 5 for name in columns}
        records.append(record)
    return pd.DataFrame(records, columns=columns).to_csv(index=False).encode("utf-8")


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.payload


def test_load_raw_data_from_local_fixture(tmp_path):
    path = tmp_path / "heart.csv"
    path.write_bytes(synthetic_csv(12))
    frame = load_raw_data(path)
    assert frame.shape == (12, len(EXPECTED_COLUMNS))
    assert frame.columns.tolist() == EXPECTED_COLUMNS


def test_load_raw_data_rejects_missing_column(tmp_path):
    path = tmp_path / "invalid.csv"
    path.write_bytes(synthetic_csv(12, drop_column="target"))
    with pytest.raises(ValueError, match="Missing"):
        load_raw_data(path)


def test_download_falls_back_after_bad_mirror_without_network(tmp_path):
    destination = tmp_path / "nested" / "heart.csv"
    calls = []

    def fake_open(url, timeout):
        calls.append((url, timeout))
        payload = synthetic_csv(12) if len(calls) == 1 else synthetic_csv()
        return FakeResponse(payload)

    with patch.object(data, "urlopen", side_effect=fake_open):
        assert download_dataset(destination) == destination

    assert len(calls) == 2
    assert [url for url, _ in calls] == data.DATA_MIRRORS[:2]
    assert all(timeout == 30 for _, timeout in calls)
    assert load_raw_data(destination).shape[0] == 1025


def test_download_cleans_partial_file_when_all_mirrors_fail(tmp_path):
    destination = tmp_path / "heart.csv"
    with patch.object(data, "urlopen", return_value=FakeResponse(synthetic_csv(8))) as opener:
        with pytest.raises(RuntimeError, match="Could not download dataset"):
            download_dataset(destination)
    assert opener.call_count == len(data.DATA_MIRRORS)
    assert not destination.exists()
