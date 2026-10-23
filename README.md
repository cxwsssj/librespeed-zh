![LibreSpeed Logo](https://github.com/librespeed/speedtest/blob/master/.logo/logo3.png?raw=true)

# LibreSpeed 简体中文版

基于 [librespeed/speedtest](https://github.com/librespeed/speedtest) 的自用 fork，在保留上游全部测速能力的前提下，提供**简体中文界面**，并每天自动跟随上游更新。

- 上游项目：https://github.com/librespeed/speedtest
- 本仓库：https://github.com/cxwsssj/librespeed-zh
- 许可证：LGPL-3.0（与上游一致）

## 特性

- 下载 / 上传 / 延迟 / 抖动测试，现代版星空 UI
- 遥测与结果统计页（SQLite / MySQL / PostgreSQL / MSSQL，可选）
- 结果分享（PNG 图片 + JSON API）
- 连接稳定性测试（延迟曲线、丢包率、阈值告警、CSV 导出）
- 多测速节点（M-POT），以及官方 CLI / Android / .NET 客户端兼容
- 简体中文覆盖：主页、按钮与状态、隐私政策、稳定性页、统计页

## 中文实现方式

**不修改上游任何文件**，中文内容单独放在覆盖层里，避免自动同步时产生合并冲突：

```
i18n/zh-CN/                         中文覆盖层（提交到仓库）
  index-modern.html                 测速主页
  speedtest.js                      少量报错文案
  stability.html                    稳定性测试页
  frontend/javascript/index.js      按钮、状态、分享等动态文案
  results/stats.php                 统计页
scripts/zh_translate.py             翻译规则与生成脚本（翻译的唯一来源）
Dockerfile.zh                       基于官方镜像叠加中文覆盖层
.github/workflows/sync-upstream.yml 每日同步上游并重新生成中文
```

`Dockerfile.zh` 把中文文件复制到镜像的 `/speedtest/` 源目录；容器启动时，官方 entrypoint 会照常把它们复制进 web 根目录。

## 直接拉取（推荐给使用者）

镜像已发布到 GitHub Container Registry（GHCR，公开，可匿名拉取，无需登录）：

```bash
docker pull ghcr.io/cxwsssj/librespeed-zh:latest
```

`compose.yaml` 示例：

```yaml
services:
  librespeed:
    image: ghcr.io/cxwsssj/librespeed-zh:latest
    container_name: librespeed
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      MODE: standalone
      USE_NEW_DESIGN: "true"
      TELEMETRY: "true"
      ENABLE_ID_OBFUSCATION: "true"
      PASSWORD: "统计页密码"
      GDPR_EMAIL: "privacy@example.com"
    volumes:
      - ./db:/database
```

```bash
docker compose pull
docker compose up -d
```

- 架构：`linux/amd64`、`linux/arm64`
- 标签：`latest`、`sha-<短提交>`；打 `v*` tag 时还会生成版本号标签
- 发布流程：`.github/workflows/publish-zh.yml`，每次 push 到 `master` 自动构建并推送

## 自己构建

```bash
docker build -f Dockerfile.zh -t librespeed-zh:latest .
```

Docker Compose 示例：

```yaml
services:
  librespeed:
    image: librespeed-zh:latest
    build:
      context: .
      dockerfile: Dockerfile.zh
    container_name: librespeed
    restart: unless-stopped
    ports:
      - "127.0.0.1:8090:8080"
    environment:
      MODE: standalone
      USE_NEW_DESIGN: "true"
      TELEMETRY: "true"
      ENABLE_ID_OBFUSCATION: "true"
      PASSWORD: "统计页密码"
      GDPR_EMAIL: "privacy@example.com"
    volumes:
      - ./db:/database
```

注意：

- 标题与副标题已写死在 `i18n/zh-CN/index-modern.html` 中，官方 entrypoint 的 `TITLE` / `TAGLINE` 环境变量不再生效。
- 开启 `TELEMETRY` 后，结果保存在 `/database/db.sql`（默认 SQLite），统计页为 `/results/stats.php`。
- 经典版界面（`index-classic.html`）未汉化，本项目只针对现代版 UI。

## 反向代理

放在 Nginx / NPM 后面时：

- 允许较大的 POST 请求体（上传测速，建议 ≥ 35 MB）；
- 代理超时大于 60 秒；
- 高带宽环境下建议对该站点关闭 `proxy_buffering`，避免测速数据被缓冲到临时文件。

## 每日自动同步

`.github/workflows/sync-upstream.yml` 每天 **04:17 UTC（北京时间 12:17）** 执行：

1. 合并 `librespeed/speedtest` 的 `master`；
2. 重新运行 `scripts/zh_translate.py` 生成 `i18n/zh-CN/`；
3. 提交并推送更新。

`README.md` 通过 `.gitattributes` 的 `merge=ours` 保留本仓库版本，不会被上游 README 覆盖。

fork 仓库首次使用时，如果 Actions 没有自动运行，需要在 Actions 页面手动启用一次，或手动触发 `Sync upstream`。

## 翻译维护

```bash
python3 scripts/zh_translate.py
```

- 全部匹配：输出 `All translations applied cleanly.`
- 出现 `WARN`：上游英文文案有变动，在 `scripts/zh_translate.py` 对应文件的规则里补一条翻译即可。

## 与上游的差异

- 增加 `i18n/zh-CN/`、`scripts/zh_translate.py`、`Dockerfile.zh`、同步工作流和本说明；
- 不修改上游的 HTML / JS / PHP 源文件；
- 未改动测速协议与后端接口，官方客户端仍可正常对接。

## 致谢与许可

测速引擎、后端与原始界面来自 [LibreSpeed](https://github.com/librespeed/speedtest)，作者 Federico Dossena 及贡献者。

Copyright (C) 2016-2024 Federico Dossena

本程序为自由软件，依据 GNU Lesser General Public License v3 或更新版本发布；本仓库的中文覆盖层同样采用 LGPL-3.0。详见 [LICENSE](LICENSE)。
