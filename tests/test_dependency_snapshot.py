"""Offline regression tests for dependency artifact validation."""

import hashlib
from pathlib import Path
from zipfile import ZipFile

import pytest

from scripts.validate_dependency_snapshot import validate


def snapshot(tmp_path: Path, text: str):
    archive = tmp_path / "snapshot.zip"
    with ZipFile(archive, "w") as z:
        z.writestr("python311-ubuntu2404-freeze.txt", text)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    return archive, digest


def test_valid_exact_pins(tmp_path):
    archive, digest = snapshot(tmp_path, "numpy==2.1.0\npandas==2.2.0\n")
    assert validate(archive, digest, "python311-ubuntu2404-freeze.txt") == 2


@pytest.mark.parametrize("bad", [
    "numpy==2.1 0",
    "numpy==2.1\t0",
    "numpy>=2.1",
    "numpy==2.1\nnumpy==2.2",
    "numpy==2.1\nNum_py==2.2\nnum-py==2.3",
])
def test_invalid_pins(tmp_path, bad):
    archive, digest = snapshot(tmp_path, bad)
    with pytest.raises(ValueError):
        validate(archive, digest, "python311-ubuntu2404-freeze.txt")


def test_digest_mismatch(tmp_path):
    archive, _ = snapshot(tmp_path, "numpy==2.1.0")
    with pytest.raises(ValueError, match="mismatch"):
        validate(archive, "0" * 64, "python311-ubuntu2404-freeze.txt")


def test_missing_member(tmp_path):
    archive, digest = snapshot(tmp_path, "numpy==2.1.0")
    with pytest.raises(ValueError, match="exactly one"):
        validate(archive, digest, "missing.txt")


def test_empty_freeze_rejected(tmp_path):
    archive, digest = snapshot(tmp_path, "# no packages\n\n")
    with pytest.raises(ValueError, match="no package pins"):
        validate(archive, digest, "python311-ubuntu2404-freeze.txt")


def test_normalized_duplicate_rejected(tmp_path):
    archive, digest = snapshot(tmp_path, "my_pkg==1.0\nMY.PKG==1.1\n")
    with pytest.raises(ValueError, match="Duplicate normalized package"):
        validate(archive, digest, "python311-ubuntu2404-freeze.txt")


def test_invalid_digest_format_rejected(tmp_path):
    archive, _ = snapshot(tmp_path, "numpy==2.1.0\n")
    with pytest.raises(ValueError, match="64 hexadecimal"):
        validate(archive, "not-a-sha256", "python311-ubuntu2404-freeze.txt")


def test_corrupt_zip_member_rejected(tmp_path):
    archive, _ = snapshot(tmp_path, "numpy==2.1.0\n")
    raw = archive.read_bytes()
    assert raw.count(b"numpy==2.1.0") == 1
    archive.write_bytes(raw.replace(b"numpy==2.1.0", b"numpx==2.1.0"))
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="CRC"):
        validate(archive, digest, "python311-ubuntu2404-freeze.txt")
