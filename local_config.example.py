# -*- coding: utf-8 -*-
"""Agnes MCP 本地配置模板。

使用方法：
  1. 复制本文件为 local_config.py（与 agnes_mcp_server.py 同目录）；
  2. 把 API_KEY 改成你自己的 Agnes API Key；
  3. 保存即可运行。

⚠️ local_config.py 已被 .gitignore 忽略，不会上传到 GitHub，请放心填写。
"""

# Agnes 平台 API Key（必填）
API_KEY = "sk-你的AgnesAPIKey"

# Agnes API 基础地址（一般不用改）
BASE_URL = "https://api.agnes-ai.cn/v1"

# 生成结果保存目录；None 表示脚本同目录下的 output/ 文件夹
# 示例：OUTPUT_DIR = r"D:\projects\agnes-mcp\output"
OUTPUT_DIR = None

# 图片 / 视频模型（一般不用改）
IMAGE_MODEL = "agnes-image-2.1-flash"
VIDEO_MODEL = "agnes-video-2.5-flash"
