from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from data import download_dataset, load_raw_data  # noqa: E402


def main() -> None:
    destination = ROOT / "data" / "heart_data.csv"
    path = download_dataset(destination)
    df = load_raw_data(path)
    print(f"Downloaded dataset to: {path}")
    print(f"Shape: {df.shape}")
    print(f"Duplicate rows: {df.duplicated().sum()}")


if __name__ == "__main__":
    main()
