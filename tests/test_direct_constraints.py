"""Guard the experimental direct pins against requirements.txt drift."""

from pathlib import Path

import pytest
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from packaging.version import Version

ROOT = Path(__file__).resolve().parents[1]


def _parse(lines, *, exact):
    packages = {}
    for number, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        requirement = Requirement(line)
        name = canonicalize_name(requirement.name)
        assert name not in packages, f'duplicate {name} on line {number}'
        assert not requirement.url and not requirement.marker and not requirement.extras
        if exact:
            specs = list(requirement.specifier)
            assert len(specs) == 1 and specs[0].operator == '==', f'{name} is not exactly pinned'
            assert '*' not in specs[0].version
            Version(specs[0].version)
        packages[name] = requirement
    assert packages, 'dependency inventory is empty'
    return packages


def test_candidate_covers_and_satisfies_all_direct_requirements():
    requirements = _parse((ROOT / 'requirements.txt').read_text().splitlines(), exact=False)
    constraints = _parse((ROOT / 'constraints/python311-direct-candidate.txt').read_text().splitlines(), exact=True)
    assert constraints.keys() == requirements.keys(), (
        f'missing pins: {sorted(requirements.keys() - constraints.keys())}; '
        f'extra pins: {sorted(constraints.keys() - requirements.keys())}'
    )
    for name, requirement in requirements.items():
        version = next(iter(constraints[name].specifier)).version
        assert Version(version) in requirement.specifier, f'{name}=={version} violates {requirement.specifier}'


@pytest.mark.parametrize('lines', [
    ['numpy==1.0', 'NumPy==1.1'],
    ['numpy>=1.0'],
    ['numpy==1.*'],
    ['numpy==1.0; python_version >= "3.11"'],
])
def test_invalid_exact_candidate_lines_rejected(lines):
    with pytest.raises((AssertionError, ValueError)):
        _parse(lines, exact=True)
