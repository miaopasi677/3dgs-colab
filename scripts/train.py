#!/usr/bin/env python3
"""Thin wrapper around official gaussian-splatting train.py.

Why a wrapper instead of editing the engine:
  - official defaults (learning rates, SH degree, opacity reset) are tuned;
  - we only change iteration count / densification for quality presets;
  - the same command works in Colab and in Docker.

Usage:
    python scripts/train.py --scene data/tandt/truck --preset standard
    python scripts/train.py --scene data/my_room --preset high --iterations 30000
"""
import argparse
import subprocess
import sys
from pathlib import Path

PRESETS = {
    # preview only: use it to verify data / COLMAP, not to judge quality
    "fast": {
        "iterations": 7000,
        "densification_interval": 100,
        "densify_until_iter": 5000,
    },
    # default: official 30k recipe, good for the truck example and indoor rooms
    "standard": {
        "iterations": 30000,
        "densification_interval": 100,
        "densify_until_iter": 15000,
    },
    # detail-heavy indoor scenes: densify more often and longer
    "high": {
        "iterations": 30000,
        "densification_interval": 50,
        "densify_until_iter": 20000,
    },
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", required=True, help="Scene dir, e.g. data/tandt/truck")
    ap.add_argument("--engine-dir", default="gaussian-splatting",
                    help="Checkout of graphdeco-inria/gaussian-splatting")
    ap.add_argument("--output", default=None, help="Output dir, default output/<scene-name>")
    ap.add_argument("--preset", choices=PRESETS, default="standard")
    ap.add_argument("--iterations", type=int, default=None, help="Override preset iterations")
    ap.add_argument("--eval", action="store_true", default=True,
                    help="Run evaluation (PSNR/SSIM/LPIPS on test views)")
    args = ap.parse_args()

    scene = Path(args.scene)
    if not (scene / "images").exists():
        print(f"ERROR: {scene}/images not found. Put photos in <scene>/input/ and run COLMAP first,")
        print("or run: python scripts/download_example.py")
        return 2
    if not (scene / "sparse" / "0" / "points3D.bin").exists():
        print(f"WARNING: {scene}/sparse/0/points3D.bin not found.")
        print("Official train.py needs COLMAP sparse output. Run scripts/run_colmap.sh first.")

    preset = dict(PRESETS[args.preset])
    if args.iterations is not None:
        preset["iterations"] = args.iterations
    output = args.output or f"output/{scene.name}"

    cmd = [
        sys.executable, str(Path(args.engine_dir) / "train.py"),
        "-s", str(scene),
        "-m", output,
        "--iterations", str(preset["iterations"]),
        "--densification_interval", str(preset["densification_interval"]),
        "--densify_until_iter", str(preset["densify_until_iter"]),
        "--test_iterations", "7000", "30000",
        "--save_iterations", "7000", "30000",
        "--checkpoint_iterations", "30000",
    ]
    if args.eval:
        cmd.append("--eval")
    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd)
    if result.returncode != 0:
        return result.returncode
    print(f"\nDone. Point cloud: {output}/point_cloud/iteration_{preset['iterations']}/point_cloud.ply")
    print("Render it with the engine render.py, or open the .ply in SuperSplat (see viewer/README.md).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
