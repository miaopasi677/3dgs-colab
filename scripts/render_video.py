#!/usr/bin/env python3
"""Make a rotating comparison video from official render.py output.

1. Run the engine render step first (or let the notebook do it):
       python gaussian-splatting/render.py -m output/truck
   This writes output/truck/renders/*.png (and *_gt.png for test views).
2. Then:
       python scripts/render_video.py --renders output/truck/renders --out output/truck/render.mp4
Requires ffmpeg on PATH (present in Colab and in the Dockerfile).
"""
import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--renders", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fps", type=int, default=24)
    args = ap.parse_args()

    renders = Path(args.renders)
    # Prefer rendered views without ground-truth suffix for a clean video.
    frames = sorted(p for p in renders.glob("*.png") if not p.name.endswith("_gt.png"))
    if not frames:
        print(f"No renders found in {renders}. Run render.py first.")
        return 1
    print(f"Found {len(frames)} frames, first: {frames[0].name}")
    cmd = [
        "ffmpeg", "-y", "-framerate", str(args.fps),
        "-pattern_type", "glob", "-i", str(renders / "*.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", args.out,
    ]
    # Use a simple glob pattern; ffmpeg sorts alphabetically, matching render order.
    result = subprocess.run(cmd)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
