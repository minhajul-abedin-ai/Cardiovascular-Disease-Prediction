"""Static guards for the experimental resolved-environment snapshot.

These checks validate inventory syntax and direct-requirement compatibility.
They do not establish transitive dependency closure or artifact integrity.
"""

from pathlib import Path

import pytest
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from packaging.version import Version

ROOT = Path(__file__).resolve().parents[1]


def parse_snapshot(lines):
    pins = {}
    for line_number, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        requirement = Requirement(line)
        name = canonicalize_name(requirement.name)
        assert name not in pins, f"duplicate snapshot pin {name} at line {line_number}"
        assert not requirement.extras and not requirement.marker and not requirement.url
        specifiers = list(requirement.specifier)
        assert len(specifiers) == 1 and specifiers[0].operator == "==", (
            f"{name} must have one exact version pin"
        )
        version = specifiers[0].version
        assert "*" not in version, f"{name} has a wildcard version"
        pins[name] = Version(version)
    assert pins, "snapshot contains no package pins"
    return pins


def test_snapshot_covers_direct_requirements():
    snapshot = parse_snapshot(
        (ROOT / "constraints/python311-transitive-snapshot.txt").read_text().splitlines()
    )
    direct = {}
    for raw in (ROOT / "requirements.txt").read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        requirement = Requirement(line)
        name = canonicalize_name(requirement.name)
        assert name not in direct, f"duplicate direct requirement {name}"
        direct[name] = requirement

    assert direct, "requirements.txt is empty"
    missing = sorted(direct.keys() - snapshot.keys())
    assert not missing, f"snapshot missing direct dependencies: {missing}"
    for name, requirement in direct.items():
        assert snapshot[name] in requirement.specifier, (
            f"{name}=={snapshot[name]} violates {requirement.specifier}"
        )


@pytest.mark.parametrize("lines", [
    ["numpy==1.0", "NumPy==1.1"],
    ["numpy>=1.0"],
    ["numpy==1.*"],
    ['numpy==1.0; python_version >= "3.11"'],
    ["numpy==1.0", "numpy[extra]==1.0"],
])
def test_invalid_snapshot_lines_rejected(lines):
    with pytest.raises((AssertionError, ValueError)):
        parse_snapshot(lines)
