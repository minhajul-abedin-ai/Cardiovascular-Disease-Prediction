"""Report installed dependency parents for packages absent from a candidate snapshot.

Diagnostic only: requirements may be conditional on extras, platform or Python version.
"""
from importlib.metadata import distributions
from pathlib import Path
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

snapshot = Path("constraints/python311-reduced-candidate.txt")
expected = {
    canonicalize_name(Requirement(line).name)
    for raw in snapshot.read_text().splitlines()
    if (line := raw.strip()) and not line.startswith("#")
}
installed = list(distributions())
actual = {
    canonicalize_name(dist.metadata["Name"]): dist for dist in installed
}
unexpected = sorted(set(actual) - expected - {"pip", "setuptools"})
print(f"Unexpected packages ({len(unexpected)}): {', '.join(unexpected) or 'none'}")
for name in unexpected:
    print(f"\n{name}=={actual[name].version}")
    parents = []
    for parent_name, parent in sorted(actual.items()):
        for raw in parent.requires or ():
            try:
                requirement = Requirement(raw)
            except ValueError:
                continue
            if canonicalize_name(requirement.name) == name:
                marker = str(requirement.marker) if requirement.marker else "unconditional"
                parents.append(f"{parent_name}: {raw} [marker: {marker}]")
    for parent in parents:
        print(f"  declared by {parent}")
    if not parents:
        print("  No installed distribution declares this dependency")
print("\nDiagnostic only: marker/extras applicability has not been evaluated.")
