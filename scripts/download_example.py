#!/usr/bin/env python3
"""Download the official Tanks and Temples example used by gaussian-splatting.

Source: https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/datasets/input/tandt_db.zip
This is the small, COLMAP-ready example from the official README, so the
first Colab run does not need a local COLMAP step.
"""
import argparse
import hashlib
import sys
import urllib.request
import zipfile
from pathlib import Path

URL = "https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/datasets/input/tandt_db.zip"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data", help="Directory to extract into")
    ap.add_argument("--url", default=URL)
    args = ap.parse_args()

    data_dir = Path(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    zip_path = data_dir / "tandt_db.zip"

    if not (data_dir / "tandt" / "truck" / "images").exists():
        print(f"Downloading {args.url} ...")
        urllib.request.urlretrieve(args.url, zip_path)
        print(f"Downloaded {zip_path} ({zip_path.stat().st_size / 1e6:.1f} MB)")
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(data_dir)
        print(f"Extracted to {data_dir / 'tandt'}")
    else:
        print("Example already present, skip download.")

    truck = data_dir / "tandt" / "truck"
    checks = [
        truck / "images",
        truck / "sparse" / "0" / "cameras.bin",
        truck / "sparse" / "0" / "images.bin",
        truck / "sparse" / "0" / "points3D.bin",
    ]
    missing = [str(p) for p in checks if not p.exists()]
    if missing:
        print("Missing after download/extract:", *missing, sep="\n  ")
        return 1
    n_images = len(list((truck / "images").glob("*")))
    print(f"OK: {truck} with {n_images} images, COLMAP sparse/0 present.")
    print("Next: python scripts/train.py --scene data/tandt/truck --preset standard")
    return 0


if __name__ == "__main__":
    sys.exit(main())
