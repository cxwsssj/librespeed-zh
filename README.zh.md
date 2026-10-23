# LibreSpeed 简体中文版

本仓库是 [librespeed/speedtest](https://github.com/librespeed/speedtest) 的 fork，在**不修改上游任何文件**的前提下，增加了一层简体中文覆盖层，便于持续跟随上游更新。

## 目录说明

```
i18n/zh-CN/                  由脚本生成的中文文件（提交到仓库）
  index-modern.html         测速主页
  speedtest.js              少量报错文案
  stability.html            稳定性测试页
  frontend/javascript/index.js  按钮、状态、分享等动态文案
  results/stats.php         统计页
scripts/zh_translate.py     翻译规则 + 生成脚本（翻译的唯一来源）
Dockerfile.zh               基于官方镜像叠加中文覆盖层
.github/workflows/sync-upstream.yml  每天自动合并上游并重生成中文文件
```

## 为什么用覆盖层

上游没有 i18n 机制。若直接修改上游文件，自动同步时必然产生合并冲突；因此这里把中文版放在 `i18n/zh-CN/`，由 `Dockerfile.zh` 在构建时复制到镜像的 `/speedtest/` 源目录，容器启动时官方 entrypoint 会照常把它复制进 web 根目录。

上游更新时，GitHub Actions 会自动：

1. 合并 `librespeed/speedtest` 的 `master`；
2. 重新运行 `scripts/zh_translate.py`；
3. 提交更新后的 `i18n/zh-CN/`。

如果上游改了某条英文文案，脚本会打印 `WARN` 并以非零码退出，Action 里会出现 warning 提示——此时在 `scripts/zh_translate.py` 对应文件的规则里补一条新翻译即可。

## 本地生成 / 校验

```bash
python3 scripts/zh_translate.py
```

无输出即全部匹配；出现 `WARN` 说明上游文案变了，需要更新规则。

## 构建与运行

```bash
docker build -f Dockerfile.zh -t librespeed-zh:latest .
docker run -d --name librespeed \
  -p 127.0.0.1:8090:8080 \
  -e MODE=standalone \
  -e USE_NEW_DESIGN=true \
  -e TELEMETRY=true \
  -e PASSWORD=你的统计页密码 \
  -v "$PWD/db:/database" \
  librespeed-zh:latest
```

页面顶部的标题写在 `i18n/zh-CN/index-modern.html` 里（`<title>` 与 `<h1>`），改完重新生成/构建即可。注意：标题改成中文后，官方 entrypoint 的 `TITLE` / `TAGLINE` 环境变量不再生效。

## 同步时间

默认每天 04:17 UTC（北京时间 12:17）检查上游。fork 仓库首次使用时，GitHub 可能默认禁用定时工作流，需要在 Actions 页面手动启用一次，或用 `workflow_dispatch` 手动触发。
