# SXUWhatEat

面向大学生的“今天吃什么”前后端分离 MVP。用户端支持邮箱注册登录、浏览餐厅/楼层/窗口/菜品、每日抽签；管理员端支持维护餐厅内容和普通用户，终极管理员可管理管理员账号。

## Structure

- `backend/`: FastAPI + SQLAlchemy + Alembic + MySQL
- `frontend/`: Next.js App Router + TypeScript + Tailwind CSS

## 一键启动

完成后端 `.env`、Python 虚拟环境和前端 `node_modules` 的首次配置后，在项目根目录运行：

```bash
./start.sh
```

脚本会检查 3000/8000 端口、执行 Alembic 数据库迁移，并同时启动 FastAPI 和 Next.js。终端会显示本机及局域网访问地址；按 `Ctrl+C` 会同时关闭脚本启动的两个服务。

脚本不会自动安装依赖或覆盖 `.env`。端口已被其他程序占用时会显示占用进程并安全退出。

## Backend

```bash
cd backend
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
cp .env.example .env
```

编辑 `backend/.env`，填入本机 MySQL 连接、`SECRET_KEY`、`SUPER_ADMIN_EMAIL` 和 `SUPER_ADMIN_PASSWORD`。真实密码只放 `.env`，不要提交。

启动开发服务：

```bash
cd backend
.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

运行迁移与开发种子数据：

```bash
cd backend
.venv/bin/alembic upgrade head
.venv/bin/python scripts/seed_dev.py
```

运行测试：

```bash
cd backend
.venv/bin/python -m pytest -q
```

## Frontend

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

默认前端地址为 `http://localhost:3000`，后端 API 地址为 `http://localhost:8000/api`。

同一局域网内的其他设备可使用开发机 IP 访问，例如 `http://192.168.x.x:3000`。前端通过 Next.js 同源代理访问后端，因此不需要在其他设备上配置 `localhost:8000`。

## First Super Admin

后端仅在数据库中尚无超级管理员时读取 `SUPER_ADMIN_EMAIL` 和 `SUPER_ADMIN_PASSWORD` 完成初始化，不会在每次启动时重置密码或覆盖已完成的权限转让。超级管理员可以在 `/admin` 创建、停用和删除基本管理员，并可把超级管理员权限原子转让给一名启用中的基本管理员。

基本管理员和超级管理员拥有相同的内容管理权限，均可查看管理员列表和项目操作日志；只有超级管理员可以控制管理员账号。管理员密码校验通过后还需要完成邮箱验证码二次验证。

## Email Verification

普通用户注册需要先调用“发送验证码”。后端从 `SMTP_HOST`、`SMTP_PORT`、`SMTP_SECURE`、`SMTP_USER`、`SMTP_PASS` 和 `MAIL_FROM` 读取邮件配置。只有 `ENVIRONMENT=test` 会返回 `dev_code`；development 和 production 环境必须配置 SMTP，且不会在响应中返回验证码。QQ 邮箱配置见 [docs/email-verification.md](docs/email-verification.md)。

管理员入口不会对未登录用户或普通用户显示。管理员仍可直接访问 `/admin`，但后端接口会继续校验 `ADMIN` 或 `SUPER_ADMIN` 权限。

浏览器登录状态使用 `HttpOnly`、`SameSite=Lax` Cookie，访问令牌不写入 `localStorage`。退出登录会递增账号会话版本，使旧令牌立即失效。生产环境必须配置至少 32 位的 `SECRET_KEY`，并建议仅通过 HTTPS 提供服务。

管理端支持地点、餐厅、楼层、店铺/窗口、菜品和标签的增删查改，支持上传替换店铺与菜品图片。项目日志记录管理员对管理接口的新增、编辑、删除和权限转让操作，不记录请求正文、密码或邮箱授权码。

每日随机不接受餐厅、楼层、窗口或标签筛选；系统会从所有启用窗口下的可用菜品中抽取，并为每个用户保留当天第一次抽取结果。
