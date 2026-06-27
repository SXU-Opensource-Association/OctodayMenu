# SXUWhatEat 项目启动脚本设计

## 目标

在项目根目录提供 `start.sh`，用一个前台命令启动 FastAPI 和 Next.js 开发服务，并支持本机与局域网访问。

## 启动流程

1. 定位脚本所在的项目根目录，不依赖调用者当前目录。
2. 检查 `backend/.env`、`backend/.venv/bin/python`、`backend/.venv/bin/uvicorn`、`frontend/node_modules` 和 `npm`。
3. 检查 8000、3000 端口；任一端口被占用时退出并显示占用信息，不结束已有进程。
4. 在后端目录执行 `alembic upgrade head`，失败则停止启动。
5. FastAPI 使用 `0.0.0.0:8000` 和 reload 模式启动。
6. Next.js 通过 `npm run dev -- --port 3000` 启动；项目脚本已配置监听 `0.0.0.0`。
7. 输出 localhost 地址和自动检测到的局域网 IPv4 地址。
8. 任一子进程异常退出时结束另一个进程并返回非零状态。
9. 用户按 `Ctrl+C` 时向两个进程发送终止信号并等待退出，避免残留后台服务。

## 安全边界

- 脚本不读取或输出 `.env` 内容。
- 脚本不自动安装依赖，不自动创建或覆盖环境配置。
- 脚本不使用 `kill -9`，不结束非本脚本创建的进程。
- 脚本兼容 macOS 默认 Bash 3.2，不使用 Bash 4 专属语法。

## 验证

- `bash -n start.sh` 语法检查通过。
- 已占用端口时脚本安全退出。
- 释放端口后脚本可启动两个服务。
- `localhost:3000/auth/register`、局域网地址的注册页和 `/api/health` 均可访问。
- `Ctrl+C` 后 3000、8000 端口不再由脚本子进程监听。
