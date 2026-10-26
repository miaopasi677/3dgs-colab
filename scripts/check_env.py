#!/usr/bin/env python3
"""Diagnose the Colab / Docker environment before building 3DGS extensions.

Prints torch / CUDA / nvcc / GPU arch / submodule presence, and tries to
import the three CUDA extensions. Exit code is non-zero if an extension
import fails, so a notebook cell stops here instead of printing a false
"installed" message and failing later in train.py.
"""
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception as e:  # noqa: BLE001 - diagnostic helper
        return f"<unavailable: {e}>"


def main() -> int:
    import torch

    print(f"python: {sys.version.split()[0]}")
    print(f"torch: {torch.__version__} cuda={torch.cuda.is_available()} cuda_version={torch.version.cuda}")
    print(f"cuda_home: {torch.utils.cpp_extension.CUDA_HOME}")
    print(f"nvcc: {run(['nvcc', '--version']).splitlines()[-1] if shutil.which('nvcc') else 'NOT FOUND'}")
    print(f"ninja: {shutil.which('ninja') or 'NOT FOUND'}")
    if torch.cuda.is_available():
        print(f"gpu: {torch.cuda.get_device_name(0)} capability={torch.cuda.get_device_capability(0)}")
    engine = next(
        (p for p in [Path("gaussian-splatting"), Path("../gaussian-splatting"), Path("/content/gaussian-splatting")] if p.exists()),
        Path("gaussian-splatting"),
    )
    print(f"engine dir: {engine}")
    for sub in ["diff-gaussian-rasterization", "simple-knn", "fused-ssim"]:
        p = engine / "submodules" / sub
        print(f"submodule {sub}: exists={p.exists()} glm={(p / 'third_party' / 'glm').exists() if p.exists() else False}")

    failed = []
    for mod in ["diff_gaussian_rasterization", "simple_knn", "fused_ssim"]:
        try:
            __import__(mod)
            print(f"import {mod}: OK")
        except Exception as e:  # noqa: BLE001 - report, do not hide
            print(f"import {mod}: FAILED: {type(e).__name__}: {e}")
            failed.append(mod)
    if failed:
        print(f"RESULT: extensions missing: {', '.join(failed)} - do not start training, fix the build log above first.")
        return 1
    print("RESULT: all extensions import OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
