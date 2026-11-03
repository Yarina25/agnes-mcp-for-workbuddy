# Agnes MCP Server for WorkBuddy

通过 **MCP（Model Context Protocol）** 将 [Agnes AI](https://agnes-ai.cn) 的图片 / 视频生成能力接入 **WorkBuddy** 等支持 MCP 客户端的应用。

WorkBuddy 加载本服务后，对话中即可直接指挥 AI 调用工具生成图片、生成视频，无需手动切换网页。

---

## ✨ 功能特性

| 工具                       | 说明                                 |
| ------------------------ | ---------------------------------- |
| `generate_image(prompt)` | 根据提示词生成图片，自动下载到本地 `output/` 目录     |
| `generate_video(prompt)` | 根据提示词生成视频（异步任务提交 + 状态轮询），完成后下载 mp4 |

其他特性：

- ✅ 纯本地运行，只需一个 `python` 脚本 + WorkBuddy 配置，无需搭建服务器
- ✅ 生成结果同时返回**在线链接**和**本地保存路径**
- ✅ API Key 通过本地配置文件 / 环境变量注入，**不会上传到 GitHub**
- ✅ 图片接口兼容 `data[0].url` 与 `url` 两种返回结构，报错时直接回显接口原始返回便于排查

---

## 🔧 工作原理

```
WorkBuddy (MCP Client)
        │  stdio (JSON-RPC)
        ▼
agnes_mcp_server.py  (MCP Server, FastMCP)
        │  HTTPS
        ▼
Agnes AI API (https://api.agnes-ai.cn/v1)
```

- WorkBuddy 通过 **stdio** 与本脚本通信（MCP 标准传输方式）；
- 脚本在本地调用 Agnes API 生成图片 / 视频，并把结果（链接 + 本地路径）返回给 WorkBuddy；
- 视频生成是异步流程：`提交任务 → 拿到 task_id → 每 4 秒轮询 → 完成下载`。

---

## 📁 目录结构

```
agnes-mcp-for-workbuddy/
├── agnes_mcp_server.py          # MCP 服务端主程序（两个工具）
├── local_config.example.py      # 本地配置模板（复制为 local_config.py 后填写）
├── mcp-config.example.json      # WorkBuddy MCP 配置示例
├── start_agnes_mcp.bat          # Windows 调试启动脚本（仅排查报错用）
├── requirements.txt             # Python 依赖清单
├── .gitignore                   # 忽略本地配置 / 密钥 / 产物
├── LICENSE                      # MIT 许可证
└── output/                      # （自动生成）图片、视频保存目录，已忽略不上传
```

---

## 📋 环境要求

| 项目     | 要求                                           |
| ------ | -------------------------------------------- |
| 操作系统   | Windows 10 / 11（macOS / Linux 亦可运行脚本，配置方式相同） |
| Python | 3.10 及以上                                     |
| 客户端    | WorkBuddy（支持自定义 MCP 连接器，stdio 类型）            |
| 账号     | Agnes AI 平台账号 + API Key                      |

---

## 🚀 快速开始

### 第 1 步：下载 / 克隆本项目

```cmd
git clone https://github.com/你的用户名/agnes-mcp-for-workbuddy.git
cd agnes-mcp-for-workbuddy
```

### 第 2 步：安装依赖

```cmd
pip install -r requirements.txt
```

> ⚠️ **版本锁定很重要**：`requirements.txt` 将 `mcp` 锁定为 `1.27.0`。  
> `mcp 1.30.0+` 已移除 `FastMCP` 高层装饰器，`@mcp.tool()` 写法会直接报导入错误。

### 第 3 步：配置 API Key

**方式一（推荐）：本地配置文件**

1. 复制 `local_config.example.py` 为 `local_config.py`（同目录）：
   ```cmd
   copy local_config.example.py local_config.py
   ```
2. 用记事本打开 `local_config.py`，把 `API_KEY` 改成你自己的 Key：
   ```python
   API_KEY = "sk-你的AgnesAPIKey"
   ```
3. 保存。`local_config.py` 已被 `.gitignore` 忽略，**不会随代码上传 GitHub**。

**方式二：环境变量**

```cmd
setx AGNES_API_KEY "sk-你的AgnesAPIKey"
```

设置后**重新打开** CMD 窗口才生效。

### 第 4 步：CMD 手动测试脚本（必做）

```cmd
python agnes_mcp_server.py
```

✅ **成功标志**：没有任何报错，光标停留在命令行闪烁不动（黄色 Warning 可忽略）。

❌ 如果报 `缺少 Agnes API Key`，说明第 3 步没配置好，回去检查。

### 第 5 步：在 WorkBuddy 中添加 MCP 连接器

1. 打开 WorkBuddy → 左下角 **MCP / 连接器** 面板；
2. 添加自定义连接器，传输类型选 **stdio**；
3. 参照 `mcp-config.example.json` 填写，关键字段：

| 字段      | 值                                                     |
| ------- | ----------------------------------------------------- |
| 名称      | `agnes-video`                                         |
| command | 你的 Python 完整路径（见下方说明）                                 |
| args    | `D:\你的路径\agnes-mcp-for-workbuddy\agnes_mcp_server.py` |

> **command 填什么？**
>
> - 电脑上只有一个 Python 且已加入 PATH：填 `python` 即可；
> - 有多个 Python（强烈建议填完整路径）：例如  
>   `C:\Users\你的用户名\AppData\Local\Programs\Python\Python312\python.exe`
> - 可用 `where python` 命令查到本机 Python 的完整路径。

1. 保存并**启用**该连接器；
2. **完全退出 WorkBuddy（右下角托盘右键 → 退出），再重新打开**；
3. 回到 MCP 面板，`agnes-video` 显示 **🟢 绿色圆点** 即为加载成功，工具列表里应能看到 `generate_image`、`generate_video`。

### 第 6 步：开始使用

在 WorkBuddy 对话窗口直接输入：

```
生成图片：可爱小猫，柔和光影
```

```
生成视频：小狗在草地上奔跑
```

AI 会自动调用对应工具。也可以显式指定：

```
调用 agnes-video 的 generate_image 生成图片：赛博朋克城市夜景
```

生成结果会显示在线链接，文件同时保存在项目 `output/` 目录。

> 💡 **模型选择建议**：WorkBuddy 里请选择支持 **Function Call（工具调用）** 的模型（如混元 Hy3、DeepSeek-V4-Flash 等）。纯问答型 mini 模型不会自动调用 MCP 工具。

---

## ⚙️ 配置文件说明

### `mcp-config.example.json`

```json
{
  "mcpServers": {
    "agnes-video": {
      "command": "python",
      "args": [
        "D:/projects/agnes-mcp-for-workbuddy/agnes_mcp_server.py"
      ]
    }
  }
}
```

> 这是**示例文件**，请把 `args` 里的路径换成你本机的实际路径；`command` 建议换成 Python 完整路径。

### `local_config.example.py`

| 配置项           | 说明                               | 默认值                          |
| ------------- | -------------------------------- | ---------------------------- |
| `API_KEY`     | Agnes API Key（**必填**）            | 无                            |
| `BASE_URL`    | Agnes API 基础地址                   | `https://api.agnes-ai.cn/v1` |
| `OUTPUT_DIR`  | 结果保存目录，`None` 表示脚本同目录下 `output/` | `None`                       |
| `IMAGE_MODEL` | 图片模型                             | `agnes-image-2.1-flash`      |
| `VIDEO_MODEL` | 视频模型                             | `agnes-video-2.5-flash`      |

---

## 🐛 常见问题排查

| 现象                                                          | 原因                                                          | 解决方法                                                 |
| ----------------------------------------------------------- | ----------------------------------------------------------- | ---------------------------------------------------- |
| `ModuleNotFoundError: No module named 'mcp.server.fastmcp'` | mcp 被升级到了 1.30.0+                                           | `pip install mcp==1.27.0` 降级，然后重跑脚本                  |
| `-32000 Connection closed`                                  | ① 脚本里有 `print()` 污染 stdio；② command 指向了错误的 Python；③ 脚本启动即崩溃 | 删除所有 `print()`；command 用 Python 完整路径；CMD 手动运行脚本看真实报错 |
| 启动时黄色 `IncompleteFieldDefinitionWarning`                    | FastMCP 内部依赖的无害提示                                           | 直接忽略，不影响运行                                           |
| 工具调用返回"找不到图片链接"                                             | Agnes 接口返回结构变化                                              | 脚本会回显接口原始返回 JSON，把内容发给开发者调整解析逻辑                      |
| WorkBuddy 里 MCP 是红的                                         | 进程启动失败                                                      | 双击 `start_agnes_mcp.bat` 手动运行，看控制台报错                 |
| 生成视频一直提示队列满                                                 | Agnes 服务侧限流                                                 | 稍后再试，或更换视频模型，与 MCP 配置无关                              |

### 调试用 bat（仅排查时使用）

双击 `start_agnes_mcp.bat` 会在 CMD 窗口手动启动服务，用于查看报错日志。

⚠️ **日常使用不要开 bat**：WorkBuddy 会自己拉起 Python 进程；手动开 bat + WorkBuddy 同时启动会抢占进程导致冲突。

---

## 🔐 安全说明

- 本项目 **不包含任何真实 API Key**，Key 只存在于你本地的 `local_config.py`（已被 `.gitignore` 忽略）或系统环境变量中；
- 请勿把你的 `local_config.py`、`mcp.json`（含真实路径 / Key 的配置）提交到 GitHub；
- 如果 Key 曾意外泄露，请到 Agnes 平台重新生成。

---

## 📄 License

[MIT](LICENSE)
