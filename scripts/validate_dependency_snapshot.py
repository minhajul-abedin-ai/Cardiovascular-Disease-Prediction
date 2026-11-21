"""Offline validation of a GitHub Actions pip-freeze ZIP (no installation)."""

import argparse
import hashlib
import re
import sys
from pathlib import Path
from zipfile import BadZipFile, ZipFile

PIN = re.compile(r"([A-Za-z0-9][A-Za-z0-9._-]*)==([^\\s;]+)")
NAME = re.compile(r"[-_.]+")


def validate(archive: Path, expected_sha256: str, member: str) -> int:
    if not re.fullmatch(r"[0-9a-fA-F]{64}", expected_sha256):
        raise ValueError("Expected SHA-256 must be exactly 64 hexadecimal characters")
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest != expected_sha256.lower():
        raise ValueError("Artifact SHA-256 mismatch; do not use this snapshot")
    with ZipFile(archive) as z:
        if z.namelist().count(member) != 1:
            raise ValueError(f"Expected exactly one {member} member")
        if z.testzip() is not None:
            raise ValueError("ZIP CRC verification failed")
        lines = z.read(member).decode("utf-8").splitlines()
    seen = set()
    for line_number, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = PIN.fullmatch(line)
        if not match:
            raise ValueError(f"Non-exact requirement at line {line_number}: {line!r}")
        normalized = NAME.sub("-", match.group(1)).lower()
        if normalized in seen:
            raise ValueError(f"Duplicate normalized package: {normalized}")
        seen.add(normalized)
    if not seen:
        raise ValueError("Freeze file contains no package pins")
    return len(seen)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--sha256", required=True, help="SHA-256 from GitHub artifact metadata")
    parser.add_argument("--member", default="python311-ubuntu2404-freeze.txt")
    args = parser.parse_args()
    try:
        count = validate(args.archive, args.sha256, args.member)
    except (OSError, ValueError, BadZipFile, UnicodeError) as exc:
        print(f"Snapshot validation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Validated {count} unique exact pins; archive SHA-256 matches metadata")
    print("This does not validate dependency resolution or clean installation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
