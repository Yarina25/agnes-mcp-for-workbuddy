#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agnes MCP Server for WorkBuddy（agnes-video）
=============================================

通过 MCP（Model Context Protocol）把 Agnes AI 的图片 / 视频生成能力
接入 WorkBuddy 等支持 MCP 客户端的应用。

提供两个工具：
  - generate_image(prompt)  生成图片，并自动下载到本地输出目录
  - generate_video(prompt)  生成视频（异步任务 + 轮询），完成后下载 mp4

配置方式（二选一，推荐方式一）：
  1. 复制 local_config.example.py 为 local_config.py，填入你的 API Key；
  2. 设置环境变量 AGNES_API_KEY（以及可选的 AGNES_BASE_URL /
     AGNES_OUTPUT_DIR / AGNES_IMAGE_MODEL / AGNES_VIDEO_MODEL）。

⚠️ 重要：
  - 本服务通过 stdio 与客户端通信，严禁向 stdout 输出任何 print() 内容，
    否则会污染 MCP 协议流，导致客户端报 -32000 Connection closed。
  - 依赖版本：mcp==1.27.0（FastMCP 高层 API）。
    mcp 1.30.0+ 已移除 FastMCP / MCPServer 高层装饰器，请勿升级。
"""

import asyncio
import os
import time
from pathlib import Path

import httpx
from mcp.server.fastmcp import FastMCP

# ------------------------------------------------------------------ 配置加载
try:
    # 优先读取本地配置文件 local_config.py（已被 .gitignore 忽略，不会上传）
    from local_config import (
        API_KEY,
        BASE_URL,
        OUTPUT_DIR,
        IMAGE_MODEL,
        VIDEO_MODEL,
    )
    _KEY_SOURCE = "local_config.py"
except ImportError:
    # 未配置 local_config.py 时，回退到环境变量
    API_KEY = os.environ.get("AGNES_API_KEY", "").strip()
    BASE_URL = os.environ.get("AGNES_BASE_URL", "https://api.agnes-ai.cn/v1").rstrip("/")
    OUTPUT_DIR = Path(
        os.environ.get("AGNES_OUTPUT_DIR", str(Path(__file__).resolve().parent / "output"))
    )
    IMAGE_MODEL = os.environ.get("AGNES_IMAGE_MODEL", "agnes-image-2.1-flash")
    VIDEO_MODEL = os.environ.get("AGNES_VIDEO_MODEL", "agnes-video-2.5-flash")
    _KEY_SOURCE = "环境变量 AGNES_API_KEY"

if not API_KEY:
    raise SystemExit(
        "缺少 Agnes API Key（当前来源：{}）。\n"
        "请按 README「快速开始」配置：\n"
        "  方式一：复制 local_config.example.py 为 local_config.py 并填入 API_KEY；\n"
        "  方式二：CMD 执行  setx AGNES_API_KEY \"你的Key\"  后重新打开终端。".format(_KEY_SOURCE)
    )

BASE_URL = str(BASE_URL).rstrip("/")
OUTPUT_DIR = Path(OUTPUT_DIR) if OUTPUT_DIR else Path(__file__).resolve().parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------ MCP 服务
mcp = FastMCP("agnes-video")


@mcp.tool()
async def generate_image(prompt: str) -> str:
    """生成图片
    Args:
        prompt: 图片提示词，描述你想生成的画面
    """
    async with httpx.AsyncClient(timeout=120) as cli:
        payload = {"prompt": prompt, "model": IMAGE_MODEL}
        resp = await cli.post(
            f"{BASE_URL}/images/generations",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json=payload,
        )
        try:
            res = resp.json()
        except Exception:
            return f"❌ 接口返回非 JSON，状态码:{resp.status_code}，响应原文:{resp.text[:500]}"

        # 兼容两种返回结构，优先 OpenAI 标准格式 data[0].url
        if "data" in res and isinstance(res["data"], list) and res["data"]:
            img_url = res["data"][0].get("url")
        elif "url" in res:
            img_url = res["url"]
        else:
            img_url = None

        if not img_url:
            return f"❌ 返回中找不到图片链接，原始返回：{res}"

        dl = await cli.get(img_url, timeout=120)
        save_path = OUTPUT_DIR / f"img_{int(time.time())}.png"
        with open(save_path, "wb") as f:
            f.write(dl.content)

        return f"✅ 图片生成成功\n在线链接：{img_url}\n本地保存路径：{save_path}"


@mcp.tool()
async def generate_video(prompt: str) -> str:
    """生成视频（异步任务 + 轮询）
    Args:
        prompt: 视频提示词，描述你想生成的画面
    """
    async with httpx.AsyncClient(timeout=180) as cli:
        submit_payload = {"prompt": prompt, "model": VIDEO_MODEL}
        submit_resp = await cli.post(
            f"{BASE_URL}/videos",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json=submit_payload,
        )
        try:
            submit_res = submit_resp.json()
        except Exception:
            return (
                f"❌ 提交视频任务失败，状态码:{submit_resp.status_code}，"
                f"原文:{submit_resp.text[:500]}"
            )

        task_id = submit_res.get("task_id")
        if not task_id:
            return f"❌ 没有拿到 task_id，提交返回：{submit_res}"

        # 轮询任务状态，等待视频生成完成
        max_poll = 20
        for _ in range(max_poll):
            await asyncio.sleep(4)
            query_resp = await cli.get(
                f"{BASE_URL}/videos/{task_id}",
                headers={"Authorization": f"Bearer {API_KEY}"},
            )
            query_res = query_resp.json()
            status = query_res.get("status")

            if status == "done":
                video_url = query_res.get("url")
                if not video_url:
                    return f"❌ 任务完成，但无视频链接：{query_res}"
                dl = await cli.get(video_url, timeout=300)
                save_path = OUTPUT_DIR / f"video_{int(time.time())}.mp4"
                with open(save_path, "wb") as f:
                    f.write(dl.content)
                return f"✅ 视频生成成功\n在线链接：{video_url}\n本地保存路径：{save_path}"

            if status in ("failed", "error"):
                return f"❌ 视频任务失败：{query_res}"

        return f"⏳ 轮询超时，任务仍在排队中，task_id={task_id}"


if __name__ == "__main__":
    mcp.run()
