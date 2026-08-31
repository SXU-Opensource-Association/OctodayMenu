# SXUWhatEat API Overview

Base URL: `/api`

## Auth

- `POST /auth/register`: 普通用户邮箱+密码注册。
- `POST /auth/email-verifications`: 发送注册邮箱验证码；开发环境未配置 SMTP 时返回 `dev_code`。
- `POST /auth/login`: 普通用户使用邮箱+密码登录；管理员首次提交正确密码后返回 `202` 并发送邮箱验证码，携带 `verification_code` 再次提交后完成登录。响应同时设置 HttpOnly 会话 Cookie，Bearer token 保留用于非浏览器客户端。
- `POST /auth/logout`: 注销当前会话、清除 Cookie，并使当前账号已签发的旧令牌失效。
- `GET /auth/me`: 获取当前登录用户。

## Public

- `GET /announcements`: 获取当前未失效公告；重要公告优先，最多返回 20 条。
- `GET /restaurants`: 餐厅列表，含楼层、窗口、菜品数量。
- `GET /restaurants/{id}`: 餐厅详情，含楼层、窗口、菜品、标签。
- `GET /tags`: 可用标签列表。
- `GET /dishes?restaurant_id=&tag_ids=`: 菜品查询。
- `GET /draws/today`: 获取今天已有抽签结果。
- `POST /draws/today`: 创建或返回今天抽签结果；不使用筛选条件，直接从所有可用菜品中随机抽取。

## Admin

- `GET /admin/users`: 普通用户列表。
- `PATCH /admin/users/{id}`: 修改普通用户昵称和启用状态。
- `POST /admin/users/{id}/blacklist`: 拉入黑名单，立即使该用户已有登录凭证失效并阻止再次登录。
- `DELETE /admin/users/{id}/blacklist`: 将普通用户移出黑名单。
- `POST /admin/users/{id}/mute`: 禁止普通用户发布评论、回复和评论图片；浏览与点赞不受影响。
- `DELETE /admin/users/{id}/mute`: 解除普通用户禁言。
- `GET /admin/announcements`: 查看全部公告记录，包含已失效公告。
- `POST /admin/announcements`: 发布普通或重要公告，可通过 `expires_at` 设置自动失效时间。
- `DELETE /admin/announcements/{id}`: 删除公告。
- `GET /admin/restaurants`: 管理端餐厅详情列表。
- `POST /admin/restaurants`: 创建餐厅。
- `PATCH /admin/restaurants/{id}` / `DELETE /admin/restaurants/{id}`。
- `POST /admin/restaurants/{id}/floors`: 创建楼层。
- `PATCH /admin/floors/{id}` / `DELETE /admin/floors/{id}`。
- `POST /admin/floors/{id}/stalls`: 创建窗口。
- `PATCH /admin/stalls/{id}` / `DELETE /admin/stalls/{id}`。
- `POST /admin/stalls/{id}/dishes`: 创建菜品。
- `PATCH /admin/dishes/{id}` / `DELETE /admin/dishes/{id}`。
- `GET /admin/tags` / `POST /admin/tags` / `PATCH /admin/tags/{id}` / `DELETE /admin/tags/{id}`。

## Super Admin

- `GET /admin/admins`: 管理员列表；基本管理员和超级管理员均可查看。
- `POST /admin/admins`: 超级管理员创建基本管理员。
- `PATCH /admin/admins/{id}` / `DELETE /admin/admins/{id}`: 超级管理员修改或删除基本管理员。
- `POST /admin/admins/{id}/transfer-super-admin`: 将超级管理员权限原子转让给指定的启用中基本管理员。
- `GET /admin/audit-logs`: 查看管理员操作日志。
- `POST /admin/uploads/images`: 上传管理端店铺或菜品图片，支持 JPEG、PNG、WebP，最大 5MB。
