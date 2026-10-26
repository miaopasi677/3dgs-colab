# 怎么看训练出来的 .ply

训练完成后，最重要的文件是：

```text
output/<scene>/point_cloud/iteration_30000/point_cloud.ply
```

## 最稳的方法（推荐）

1. 从 Colab / Docker 里把 `point_cloud.ply` 下载到本地。
2. 打开 SuperSplat：https://playcanvas.com/supersplat/editor
3. 把 `.ply` 拖进去，就能旋转、缩放、截图。
4. 给客户展示时，用 SuperSplat 导出精简后的模型或直接录屏，
   不要直接发几百 MB 的原文件。

## 网页嵌入（可选，第二步再做）

网页端高斯渲染有多个开源库（例如 GaussianSplats3D、PlayCanvas），
接口版本变化快，本仓库先不内置一个容易过期的 viewer 模板。
等你室内样板跑通后，再按当时稳定的库版本单独加一个
`viewer/index.html`，避免现在写一个打不开的演示页误导客户。
