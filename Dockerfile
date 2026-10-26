FROM nvidia/cuda:11.8.0-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    TORCH_CUDA_ARCH_LIST="7.0;7.5;8.0;8.6;8.9"

WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip git cmake build-essential \
    libglm-dev libgl1-mesa-dev libglew-dev libassimp-dev libboost-all-dev \
    libgtk-3-dev libopencv-dev libgmp-dev libmpfr-dev \
    ffmpeg colmap \
    && rm -rf /var/lib/apt/lists/*

# Official engine (pinned by commit in README if you need reproducibility;
# here we track its main branch and let the user pin it after first success).
RUN git clone --recursive https://github.com/graphdeco-inria/gaussian-splatting.git

RUN pip3 install --no-cache-dir torch==2.1.2 torchvision==0.16.2 --index-url https://download.pytorch.org/whl/cu118 \
    && pip3 install --no-cache-dir plyfile tqdm joblib

# Engine submodules (CUDA extensions). This is the slow step; cache it in the image.
RUN cd gaussian-splatting \
    && pip3 install --no-cache-dir submodules/diff-gaussian-rasterization \
    && pip3 install --no-cache-dir submodules/simple-knn \
    && pip3 install --no-cache-dir submodules/fused-ssim

COPY scripts/ /workspace/scripts/
COPY notebooks/ /workspace/notebooks/

VOLUME ["/workspace/data", "/workspace/output"]
CMD ["bash"]
