#!/usr/bin/env python3
"""Generate the Simplified Chinese overlay from upstream LibreSpeed sources.

Reads the upstream files from the repository root and writes translated copies
to i18n/zh-CN/, mirroring their original paths. Run this after syncing with
upstream; any warning means an upstream string changed and needs a new entry.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "i18n" / "zh-CN"

# (source path, [(pattern, replacement, expected_count)], regex?)
RULES = {
    "index-modern.html": [
        (r'<html lang="en">', '<html lang="zh-CN">', 1, False),
        (
            "Free and Open Source Speedtest. Run it right now in your browser, or self-host on a PHP, Golang, Rust or Node server. License: LGPL.",
            "自由开源的网络测速工具。可直接在浏览器中运行，也支持在 PHP、Go、Rust 或 Node 服务器上自建。LGPL 许可证。",
            1,
            False,
        ),
        (
            "<title>LibreSpeed - Free and Open Source Speedtest</title>",
            "<title>fxm-speedtest - 自由开源测速</title>",
            1,
            False,
        ),
        (
            "<h1>Free and Open Source Speedtest.</h1>",
            "<h1>自由开源测速</h1>",
            1,
            False,
        ),
        (
            '<p class="tagline">No Flash, No Java, No Websockets, No Bullsh*t</p>',
            '<p class="tagline">无需 Flash、Java、WebSocket，没有废话</p>',
            1,
            False,
        ),
        ('alt="select..."', 'alt="选择服务器"', 1, False),
        ("<p>current server</p>", "<p>当前服务器</p>", 1, False),
        ("searching nearest server...", "正在查找最近的服务器…", 1, False),
        (
            "by clicking the start button you agree to our privacy policy",
            "点击开始按钮即表示你同意我们的隐私政策",
            1,
            False,
        ),
        ("or choose your privacy options", "或自定义隐私选项", 1, False),
        ('<span class="label">Ping</span>', '<span class="label">延迟</span>', 1, False),
        ("<h2>Download</h2>", "<h2>下载</h2>", 1, False),
        ("<h2>Upload</h2>", "<h2>上传</h2>", 1, False),
        ('<span class="label">Jitter</span>', '<span class="label">抖动</span>', 1, False),
        ("Share results", "分享结果", 1, False),
        (">stability test<", ">稳定性测试<", 1, False),
        (">source code<", ">源代码<", 1, False),
        ('alt="Close"', 'alt="关闭"', 2, False),
        ('alt="Test results in graphical form"', 'alt="测速结果图"', 1, False),
        (">Copy link<", ">复制链接<", 1, False),
        (">Privacy Policy<", ">隐私政策<", 1, False),
        (
            "This HTML5 speed test server is configured with telemetry enabled.",
            "本 HTML5 测速服务器已开启遥测（结果记录）。",
            1,
            False,
        ),
        ("What data we collect", "我们收集哪些数据", 1, False),
        (
            "At the end of the test, the following data is collected and stored:",
            "测速结束后，会收集并保存以下数据：",
            1,
            False,
        ),
        ("<li>Test ID</li>", "<li>测试 ID</li>", 1, False),
        ("<li>Time of testing</li>", "<li>测试时间</li>", 1, False),
        (
            "<li>Test results (download and upload speed, ping and jitter)</li>",
            "<li>测试结果（下载/上传速度、延迟、抖动）</li>",
            1,
            False,
        ),
        ("<li>IP address</li>", "<li>IP 地址</li>", 1, False),
        ("<li>ISP information</li>", "<li>运营商信息</li>", 1, False),
        (
            "<li>Approximate location (inferred from IP address, not GPS)</li>",
            "<li>大致位置（根据 IP 推断，非 GPS）</li>",
            1,
            False,
        ),
        ("<li>User agent and browser locale</li>", "<li>浏览器 UA 与语言</li>", 1, False),
        (
            "<li>Test log (contains no personal information)</li>",
            "<li>测试日志（不含个人信息）</li>",
            1,
            False,
        ),
        ("How we use the data", "数据用途", 1, False),
        (
            "Data collected through this service is used to:",
            "通过本服务收集的数据用于：",
            1,
            False,
        ),
        (
            "Allow sharing of test results (sharable image for forums, etc.)",
            "生成可分享的测试结果（论坛图片等）",
            1,
            False,
        ),
        (
            r"To improve the service offered to you \(for instance, to detect\s+problems on our side\)",
            "改进服务质量（例如发现服务端问题）",
            1,
            True,
        ),
        (
            "No personal information is disclosed to third parties.",
            "不会向第三方披露任何个人信息。",
            1,
            False,
        ),
        ("Your consent", "你的同意", 1, False),
        (
            "By starting the test, you consent to the terms of this privacy policy.",
            "开始测速即表示你同意本隐私政策的条款。",
            1,
            False,
        ),
        ("Data removal", "数据删除", 1, False),
        (
            r"If you want to have your information deleted, you need to provide\s+either the ID of the test or your IP address\. This is the only way to\s+identify your data, without this information we won't be able to\s+comply with your request\.",
            "如需删除你的信息，请提供测试 ID 或 IP 地址。这是识别你数据的唯一方式，缺少这些信息我们将无法处理请求。",
            1,
            True,
        ),
        (
            "Contact this email address for all deletion requests:",
            "删除请求请联系：",
            1,
            False,
        ),
        (">Close<", ">关闭<", 1, False),
    ],
    "frontend/javascript/index.js": [
        ('"Copied!"', '"已复制！"', 1, False),
        ('"Copy link"', '"复制链接"', 2, False),
        ('"Settings are empty or malformed"', '"设置文件为空或格式错误"', 1, False),
        ('"Failed to fetch settings:"', '"读取设置失败："', 1, False),
        ('"Server list is empty or malformed"', '"服务器列表为空或格式错误"', 1, False),
        ('"Failed to load server list:"', '"加载服务器列表失败："', 1, False),
        (
            '"Can\'t reach any of the speedtest servers! But you\'re on this page. Something weird is going on with your network."',
            '"无法连接任何测速服务器，但页面却能打开，你的网络可能有问题。"',
            1,
            False,
        ),
        ('"Loading..."', '"加载中…"', 1, False),
        ('"Let\'s start"', '"开始测速"', 1, False),
        ('"Abort"', '"停止"', 1, False),
        ('"Restart"', '"重新测速"', 1, False),
        ("Sponsor: ", "赞助商：", 2, False),
        ("'You are connected through:'", "'你的网络信息：'", 1, False),
    ],
    "speedtest.js": [
        ('"You cannot change the test settings while running the test"', '"测试进行中无法修改设置"', 1, False),
        ('"Invalid server definition"', '"服务器定义无效"', 1, False),
        ('"No server is selected"', '"未选择服务器"', 1, False),
        ('"No test points added"', '"未添加测试节点"', 1, False),
        ('"Server already selected"', '"已选择该服务器"', 1, False),
        ('"Test already running"', '"测试正在进行中"', 1, False),
        ('"You cannot abort a test that\'s not started yet"', '"当前没有正在进行的测试，无法停止"', 1, False),
    ],
    "stability.html": [
        ("<title>LibreSpeed - Stability Test</title>", "<title>LibreSpeed - 稳定性测试</title>", 1, False),
        ("&larr; Speed Test", "&larr; 测速", 1, False),
        ("<option value=\"60\">60 Seconds</option>", "<option value=\"60\">60 秒</option>", 1, False),
        ("<option value=\"90\">90 Seconds</option>", "<option value=\"90\">90 秒</option>", 1, False),
        ("<option value=\"120\">2 Minutes</option>", "<option value=\"120\">2 分钟</option>", 1, False),
        ("<option value=\"180\">3 Minutes</option>", "<option value=\"180\">3 分钟</option>", 1, False),
        ("<option value=\"300\">5 Minutes</option>", "<option value=\"300\">5 分钟</option>", 1, False),
        ('<option value="">Local Server</option>', '<option value="">本地服务器</option>', 1, False),
        ('title="Finding best server..."', 'title="正在查找最佳服务器…"', 1, False),
        ('>Reset<', '>重置<', 1, False),
        ("Server:", "服务器：", 1, False),
        ('<div class="testName">Current</div>', '<div class="testName">当前</div>', 1, False),
        ('<div class="testName">Average</div>', '<div class="testName">平均</div>', 1, False),
        ('<div class="testName">Jitter</div>', '<div class="testName">抖动</div>', 1, False),
        ('<div class="testName">Min</div>', '<div class="testName">最小</div>', 1, False),
        ('<div class="testName">Max</div>', '<div class="testName">最大</div>', 1, False),
        ('<div class="testName">Failed Requests</div>', '<div class="testName">失败请求</div>', 1, False),
        ('<div class="testName">Elapsed</div>', '<div class="testName">已用时间</div>', 1, False),
        ('<span id="thresholdValue">Off</span>', '<span id="thresholdValue">关闭</span>', 1, False),
        (">Download CSV<", ">下载 CSV<", 1, False),
        (">Source code<", ">源代码<", 1, False),
        ('content: "Start";', 'content: "开始";', 1, False),
        ('content: "Finding...";', 'content: "查找中…";', 1, False),
        ('content: "Abort";', 'content: "停止";', 1, False),
        ('"Finding best server..."', '"正在查找最佳服务器…"', 2, False),
        ('"No reachable local server found"', '"未找到可用的本地服务器"', 1, False),
        ('{ text: "Great", cls: "great" }', '{ text: "优秀", cls: "great" }', 1, False),
        ('{ text: "Good", cls: "good" }', '{ text: "良好", cls: "good" }', 1, False),
        ('{ text: "Poor", cls: "poor" }', '{ text: "较差", cls: "poor" }', 1, False),
        ('{ text: "Bad", cls: "bad" }', '{ text: "很差", cls: "bad" }', 1, False),
    ],
    "results/stats.php": [
        ("<title>LibreSpeed - Stats</title>", "<title>LibreSpeed - 统计</title>", 1, False),
        ("<h1>LibreSpeed - Stats</h1>", "<h1>LibreSpeed - 统计</h1>", 1, False),
        (
            "Please set $stats_password in telemetry_settings.php to enable access.",
            "请在 telemetry_settings.php 中设置 $stats_password 以启用访问。",
            1,
            False,
        ),
        ('value="Logout"', 'value="退出登录"', 1, False),
        ("<h3>Search test results</h3>", "<h3>查询测试结果</h3>", 1, False),
        ('placeholder="Test ID"', 'placeholder="测试 ID"', 1, False),
        ('value="Find"', 'value="查询"', 1, False),
        ('value="Show last 100 tests"', 'value="显示最近 100 条"', 1, False),
        (
            "There was an error trying to fetch the test result for ID",
            "获取该 ID 的测试结果时出错",
            1,
            False,
        ),
        (
            "Could not find a test result for ID",
            "未找到该 ID 的测试结果",
            1,
            False,
        ),
        (
            "There was an error trying to fetch latest test results.",
            "获取最新测试结果时出错。",
            1,
            False,
        ),
        (
            "Could not find any test results in database.",
            "数据库中没有找到任何测试结果。",
            1,
            False,
        ),
        ("<th>Test ID</th>", "<th>测试 ID</th>", 1, False),
        ("<th>Date and time</th>", "<th>日期与时间</th>", 1, False),
        ("<th>IP and ISP Info</th>", "<th>IP 与运营商信息</th>", 1, False),
        ("<th>User agent and locale</th>", "<th>浏览器 UA 与语言</th>", 1, False),
        ("<th>Download speed</th>", "<th>下载速度</th>", 1, False),
        ("<th>Upload speed</th>", "<th>上传速度</th>", 1, False),
        ("<th>Ping</th>", "<th>延迟</th>", 1, False),
        ("<th>Jitter</th>", "<th>抖动</th>", 1, False),
        ("<th>Log</th>", "<th>日志</th>", 1, False),
        ("<th>Extra info</th>", "<th>附加信息</th>", 1, False),
        ("<h3>Login</h3>", "<h3>登录</h3>", 1, False),
        ('placeholder="Password"', 'placeholder="密码"', 1, False),
        ('value="Login"', 'value="登录"', 1, False),
    ],
}


def main() -> int:
    warnings = 0
    for rel, rules in RULES.items():
        src = ROOT / rel
        if not src.is_file():
            print(f"ERROR missing source: {rel}", file=sys.stderr)
            return 1
        text = src.read_text(encoding="utf-8")
        for pattern, repl, expected, is_regex in rules:
            if is_regex:
                text, n = re.subn(pattern, repl, text)
            else:
                n = text.count(pattern)
                if n:
                    text = text.replace(pattern, repl)
            if n != expected:
                warnings += 1
                print(
                    f"WARN {rel}: expected {expected}, found {n}: {pattern[:70]!r}",
                    file=sys.stderr,
                )
        dst = OUT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(text, encoding="utf-8")
        print(f"wrote {dst.relative_to(ROOT)}")
    if warnings:
        print(f"\n{warnings} warning(s): upstream text may have changed.", file=sys.stderr)
        return 2
    print("\nAll translations applied cleanly.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
