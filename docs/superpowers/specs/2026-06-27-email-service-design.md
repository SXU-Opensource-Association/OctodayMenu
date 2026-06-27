# SXUWhatEat 邮件服务与注册验证码设计

## 目标

为 FastAPI 后端提供可复用的普通文本邮件和 HTML 邮件发送能力，并将现有注册验证码流程接入 QQ 邮箱 SMTP。所有 SMTP 凭据只从环境变量读取，任何 API 响应和日志都不得包含 SMTP 授权码。

## 配置

后端只读取以下 SMTP 环境变量：

- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_SECURE`
- `SMTP_USER`
- `SMTP_PASS`
- `MAIL_FROM`

`SMTP_SECURE=true` 使用隐式 SSL 连接，适用于 QQ 邮箱 465 端口。`SMTP_SECURE=false` 使用普通 SMTP 连接后执行 STARTTLS，适用于 587 端口。

development 和 production 环境必须完整配置 SMTP，否则发送接口返回通用 `503` 错误。只有 `ENVIRONMENT=test` 可以跳过真实 SMTP，并在验证码接口响应中返回 `dev_code`。

## 组件

### EmailService

独立服务提供：

- `send_text(to, subject, text)`：发送普通文本邮件。
- `send_html(to, subject, html, text=None)`：发送 HTML 邮件，并附带纯文本回退内容。

服务负责构造标准 `EmailMessage`、建立 SSL 或 STARTTLS 连接、认证并发送。底层异常转换为不携带原始 SMTP 异常文本的领域异常，API 只返回通用错误。

### 验证码服务

验证码服务负责：

- 使用密码学安全随机数生成 6 位数字验证码，包括前导零。
- 验证码只保存密码哈希，原文不写入数据库。
- 有效期固定为 5 分钟。
- 发送 HTML 验证码邮件，同时提供纯文本回退内容。
- 注册成功消费验证码，已消费或过期验证码不能复用。

## 限流与发送状态

同一邮箱：

- 距最近一次发送尝试不足 60 秒时拒绝，返回 `429`。
- 最近 1 小时已有 5 次发送尝试时拒绝，返回 `429`。

限流记录保存在数据库中，因此多个应用进程共享状态。`email_verifications` 增加发送状态字段：

- 新请求先写入 `PENDING` 记录，以便发送失败也计入限流。
- SMTP 成功后更新为 `SENT`，只有 `SENT` 记录可用于注册。
- SMTP 失败后更新为 `FAILED`，该记录用于限流但不能用于注册。
- test 环境跳过 SMTP，并直接标记为 `SENT`。

验证码原文仅存在于发送请求进程内。发送失败后不会返回或持久化验证码原文。

## API 行为

现有 `POST /api/auth/email-verifications` 路径保持不变：

- 成功：`201 {"status": "sent", "dev_code": null}`。
- test 环境成功：响应允许包含 `dev_code`。
- SMTP 未配置或发送失败：通用 `503`，不返回底层异常和敏感配置。
- 触发限流：通用 `429`，分别说明一分钟或一小时限制。
- 邮箱已注册：保持现有 `409`。

现有注册接口保持不变，继续提交 `verification_code`。

## 数据迁移

新增 Alembic 迁移，为 `email_verifications` 增加 `delivery_status` 字段，默认兼容旧记录。旧记录不具备可确认的真实发送状态，因此迁移后标记为 `SENT`，避免破坏正在进行的本地注册流程。

## 测试

- `EmailService` 文本邮件正确设置主题、发件人、收件人和正文。
- HTML 邮件同时包含纯文本与 HTML 内容。
- SSL 与 STARTTLS 分支使用正确连接方式。
- SMTP 配置只从六个指定环境变量读取。
- 验证码始终为 6 位数字并在 5 分钟后失效。
- 同一邮箱 60 秒内第二次发送被拒绝。
- 同一邮箱一小时第 6 次发送被拒绝。
- SMTP 失败时记录为 `FAILED`，不能注册，且响应不泄露授权码。
- 只有 test 环境返回 `dev_code`。
- development/production 未配置 SMTP 返回通用 `503`。
- 现有注册、登录与其他后端测试保持通过。

## 手动配置

用户需要在 QQ 邮箱设置中开启 SMTP 服务并生成 16 位授权码。实际运行时填写：

```env
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_SECURE=true
SMTP_USER=你的QQ邮箱地址
SMTP_PASS=QQ邮箱生成的16位授权码
MAIL_FROM=你的QQ邮箱地址
```

`SMTP_PASS` 不是 QQ 登录密码，不应提交到 Git、截图或聊天记录中。
