# GitHub 上传完整命令清单（Windows CMD 版）

> 适用场景：把 `agnes-mcp-for-workbuddy` 项目第一次上传到 GitHub。
> 全程在 **CMD** 里执行，逐条复制粘贴即可。

---

## 第 0 步：先在 GitHub 网页新建空仓库（必做）

1. 打开 https://github.com/new 登录你的账号（Yarina25）
2. **Repository name** 填：`agnes-mcp-for-workbuddy`
3. 其他全部**保持默认 / 不勾选**：
   - ❌ 不要勾 Add a README file
   - ❌ 不要勾 Add .gitignore
   - ❌ 不要选 Choose a license
4. 点 **Create repository**
5. 建好后复制仓库地址，形如：
   `https://github.com/Yarina25/agnes-mcp-for-workbuddy.git`

> ⚠️ 为什么要建空仓库？如果网页上勾了 README，本地 push 会冲突，要多一步合并。

---

## 第 1 步：打开 CMD，进入项目文件夹

把项目解压到你想要的位置，例如 `D:\projects\Tools\agnes-mcp-for-workbuddy`，然后：

```cmd
cd /d D:\projects\Tools\agnes-mcp-for-workbuddy
```

> 路径换成你实际解压的位置。`/d` 的作用是跨盘符跳转。

---

## 第 2 步：确认 Git 身份（第一次用 Git 才需要）

如果之前提交过代码可跳过。先执行：

```cmd
git config --global user.name "Yarina25"
git config --global user.email "你的GitHub邮箱@example.com"
```

> 邮箱换成你 GitHub 账号绑定的邮箱。

---

## 第 3 步：初始化仓库并提交

逐条执行（每行一条，回车后等下一条再继续）：

```cmd
git init
```

```cmd
git add .
```

```cmd
git status
```

> ✅ **检查这一步的输出**：
> 看列表里应该有 `README.md`、`agnes_mcp_server.py`、`requirements.txt` 等；
> **绝对不能出现 `local_config.py`**（它已被 .gitignore 忽略，出现就说明配置错了，先别提交，找我排查）。

```cmd
git commit -m "initial commit: agnes mcp server for workbuddy"
```

```cmd
git branch -M main
```

---

## 第 4 步：关联远程仓库并推送

把下面命令里的仓库地址换成你第 0 步复制的：

```cmd
git remote add origin https://github.com/Yarina25/agnes-mcp-for-workbuddy.git
```

```cmd
git push -u origin main
```

---

## 第 5 步：首次推送的登录授权

第一次 push 会弹出授权窗口：

- **弹窗让你登录浏览器** → 点授权（GitHub Credential Manager），自动完成
- **CMD 里提示输入 Username / Password** →
  - Username：`Yarina25`
  - Password：**不要填登录密码**，填 Personal Access Token（PAT）

> PAT 获取：GitHub 网页 → 右上角头像 → Settings → Developer settings →
> Personal access tokens → Tokens (classic) → Generate new token →
> 勾选 `repo` 权限 → 生成后复制保存。

看到类似 `branch 'main' set up to track 'origin/main'` 就上传成功了，刷新 GitHub 网页就能看到代码。

---

## 常见报错速查

| 报错 | 原因 | 解决 |
|---|---|---|
| `src refspec main does not match any` | 还没有任何 commit | 回到第 3 步，确认 `git add .` 和 `git commit` 都执行成功 |
| `failed to push some refs ... remote contains work you do not have` | 网页上建仓库时勾了 README | 执行 `git pull origin main --allow-unrelated-histories`，再 `git push -u origin main` |
| `Authentication failed` | 密码填错了（填了网页登录密码） | 重新 push，密码处填 **PAT** |
| `remote origin already exists` | 重复关联了远程地址 | 执行 `git remote set-url origin 你的仓库地址` 再 push |
| `fatal: not a git repository` | 不在项目目录里 | 先 `cd /d` 进入项目文件夹（第 1 步） |

---

## 以后日常更新代码（改完文件后）

```cmd
cd /d D:\projects\Tools\agnes-mcp-for-workbuddy
git add .
git commit -m "说明这次改了什么"
git push
```

---

## 安全红线（务必遵守）

- ❌ **永远不要把 `local_config.py` 提交上去**（里面有你的 API Key）
- ✅ 每次 `git add .` 之后、`git commit` 之前，看一眼 `git status` 输出
- 如果 Key 已经不小心传上去了：立刻去 Agnes 平台重新生成 Key，再删 GitHub 上的旧文件并强制推送
