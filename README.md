# 3DGS Colab 示例：高斯泼溅重建

一句话：用官方 3D Gaussian Splatting，在 Colab 里先跑通一个标准示例，
拿到好的重建效果；之后换成你自己的室内照片，同一套命令就能跑。

> 引擎说明：本仓库不重写 3DGS 算法，训练引擎是官方
> `graphdeco-inria/gaussian-splatting`。本仓库做的是 Colab / Docker
> 封装、示例数据下载、质量预设和自己的照片接入流程。

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/miaopasi677/3dgs-colab/blob/main/notebooks/3dgs_colab.ipynb)

## 0. gsplat 版（当前 Colab 推荐）

官方 2023 引擎在当前 Colab（Python 3.13 / torch 2.11 / CUDA 13）上编不过 `diff-gaussian-rasterization`，三轮修复后仍失败，因此新增 gsplat 版：

- Notebook：`notebooks/3dgs_gsplat.ipynb`，Colab 一键链接：https://colab.research.google.com/github/miaopasi677/3dgs-colab/blob/main/notebooks/3dgs_gsplat.ipynb
- 训练：直接用 gsplat 官方 `examples/simple_trainer.py`（default 策略，30000 步，全分辨率 `--data_factor 1`），不自己重写训练循环
- 产物：`results/gsplat_truck/ply/point_cloud_29999.ply`，评估在 7000 / 30000 步输出 PSNR / SSIM / LPIPS
- 注意：不要装 gsplat 官方 `examples/requirements.txt` 原样，那里面钉了 torch==2.9.1，会降级 Colab 的 torch；gsplat 版 notebook 只装训练依赖，不动 torch

## 1. Colab 一键跑（推荐先跑这个）

1. 打开上面 Colab 链接，运行时类型选 **GPU**（T4 能跑，A100 / L4 更快）。
2. 按顺序点全部运行：检查 GPU → 克隆官方引擎 → 下载示例 → 训练 → 渲染对比视频。
3. 示例是官方 Tanks and Temples 的 `truck`，自带 COLMAP 稀疏重建，
   不用你先跑 COLMAP，第一次跑最不容易翻车。

训练结果在：

```text
output/truck/point_cloud/iteration_30000/point_cloud.ply
output/truck/renders/   # 渲染图
output/truck/           # 训练日志、PSNR/SSIM/LPIPS（跑 --eval 时输出）
```

把 `point_cloud.ply` 下载下来，拖进 SuperSplat
（https://playcanvas.com/supersplat/editor）就能旋转查看，
这是目前最稳的查看方式，见 `viewer/README.md`。

## 2. 重建效果的关键（先看这个再调参）

效果好不好，90% 在数据和迭代数，不在花哨参数：

- **示例先跑满 30000 步**，不要只跑 7000 步就判断效果。
  7000 步是预览，细节、反光、边缘都会糊。
- **自己的照片**：重叠 70-80%，固定焦距、固定曝光白平衡，
  绕一圈 + 三个高度 + 细节特写，见 `docs` 章节 4。
- **室内常见翻车**：纯白墙、镜面、玻璃、运动的人和宠物、
  光线中途变化。拍之前先把这些处理掉，比后期调参管用。
- **显存不够**：先把图片降到最长边 1600px 再跑，不要直接降迭代数。
- **判断标准**：看渲染图和原图对比，看测试视角 PSNR，
  更要看旋转视频里有没有漂浮点、拉丝、墙面波纹。

## 3. 质量预设

`scripts/train.py` 只是官方 `train.py` 的薄封装，参数透传：

| 预设 | 迭代数 | 用途 |
| --- | --- | --- |
| `fast` | 7000 | 流程跑通、检查数据对不对 |
| `standard` | 30000 | 默认，示例和室内首选 |
| `high` | 30000 + 更密的 densify | 细节多的室内，时间更长 |

```bash
# 示例
python scripts/train.py --scene data/tandt/truck --preset standard

# 自己的数据（先跑完 COLMAP，见第 4 节）
python scripts/train.py --scene data/my_room --preset high
```

高预设在 `scripts/train.py` 里对应：`densification_interval=50`、
`densify_until_iter=20000`，其余保持官方默认，避免把官方调好的
学习率和球谐阶数改坏。

## 4. 换成自己的室内照片

```bash
# 1. 把照片放进 data/my_room/input/（JPG，固定焦距）
# 2. 跑 COLMAP（需要本机或 Docker 里有 colmap，Colab 里 notebook 有对应 cell）
bash scripts/run_colmap.sh data/my_room

# 3. 检查 data/my_room/sparse/0/ 里有 cameras.bin / images.bin / points3D.bin
# 4. 训练
python scripts/train.py --scene data/my_room --preset standard
```

COLMAP 失败先查：照片重叠够不够、有没有变焦、
有没有大量纯白墙或镜面。不要先怀疑训练代码。

## 5. Docker 跑（本地独显机器）

```bash
docker compose up --build -d
docker compose exec 3dgs bash
# 容器内：
python scripts/download_example.py
python scripts/train.py --scene data/tandt/truck --preset standard
```

Docker 镜像基于 CUDA 11.8，宿主机需要装 NVIDIA Container Toolkit，
并用 `--gpus all`（compose 文件里已写）。

## 6. 目录结构

```text
notebooks/3dgs_colab.ipynb   # Colab 主入口
scripts/download_example.py  # 下载官方 truck 示例
scripts/train.py             # 质量预设 + 调用官方 train.py
scripts/run_colmap.sh        # 自己的照片跑 COLMAP
scripts/render_video.py      # 渲染图合成旋转对比视频
viewer/README.md             # .ply 怎么看、怎么给客户展示
Dockerfile
docker-compose.yml
requirements.txt
```

## 7. 常见问题

- **Colab 掉线 / 超时**：先跑 `fast` 确认流程，再开 `standard`；
  Colab 免费版长时间训练可能被回收，重要结果及时下载 `point_cloud.ply`。
- **CUDA 报错**：先看 `nvidia-smi` 和 `torch.cuda.is_available()`，
  Colab 里选了 CPU 运行时一定会失败。
- **扩展编译失败（`diff_gaussian_rasterization` 找不到）**：先看安装单元格的完整日志，不要只看最后一句；本仓库修复版已补 `plyfile`、去掉静默安装、定 T4 架构 `7.5`、并在安装后做导入校验，校验失败会直接停住，不会假装装好再让训练报错。
- **渲染很糊**：先确认迭代数是不是 30000，再确认是不是测试视角；
  训练视角好看、测试视角糊，说明照片覆盖不够，要补拍。
- **点云文件很大**：正常，室内 30000 步的 `.ply` 几百 MB 很常见，
  给客户展示前先压缩或用 SuperSplat 精简，不要直接发原文件。

## 许可证与来源

- 训练引擎：官方 gaussian-splatting，按其原仓库许可证使用。
- 示例数据：Tanks and Temples `truck`，按官方示例下载链接使用。
- 本仓库新增的封装脚本、notebook、Dockerfile 按 MIT 使用。
