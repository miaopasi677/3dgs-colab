#!/usr/bin/env bash
# Run COLMAP on your own photos for gaussian-splatting.
# Input layout:
#   <scene>/input/*.jpg   (fixed focal length, no zoom change during shooting)
# Output layout (what official train.py expects):
#   <scene>/images/       (undistorted images)
#   <scene>/sparse/0/     (cameras.bin, images.bin, points3D.bin)
#
# Usage: bash scripts/run_colmap.sh data/my_room
set -euo pipefail
SCENE="${1:?Usage: bash scripts/run_colmap.sh data/my_room}"
mkdir -p "$SCENE/distorted" "$SCENE/sparse" "$SCENE/images"

# 1. Feature extraction + matching + sparse reconstruction.
#    max_image_size 3200 keeps indoor detail; lower to 1600 on low VRAM / slow machines.
colmap feature_extractor \
  --database_path "$SCENE/distorted/database.db" \
  --image_path "$SCENE/input" \
  --ImageReader.single_camera 1 \
  --SiftExtraction.max_image_size 3200

colmap exhaustive_matcher \
  --database_path "$SCENE/distorted/database.db"

mkdir -p "$SCENE/distorted/sparse"
colmap mapper \
  --database_path "$SCENE/distorted/database.db" \
  --image_path "$SCENE/input" \
  --output_path "$SCENE/distorted/sparse"

# 2. Undistort into the layout gaussian-splatting expects.
colmap image_undistorter \
  --image_path "$SCENE/input" \
  --input_path "$SCENE/distorted/sparse/0" \
  --output_path "$SCENE" \
  --output_type COLMAP \
  --max_image_size 3200

echo "Done. Check: $SCENE/sparse/0/cameras.bin $SCENE/sparse/0/images.bin $SCENE/sparse/0/points3D.bin"
echo "Next: python scripts/train.py --scene $SCENE --preset standard"
