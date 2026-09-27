from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "heart_data.csv"

if not DATA.exists():
    subprocess.run([sys.executable, str(ROOT / "scripts" / "download_dataset.py")], check=True)

subprocess.run(
    [sys.executable, str(ROOT / "src" / "train.py"), "--data", str(DATA), "--output", str(ROOT / "results" / "reproduced")],
    check=True,
)
