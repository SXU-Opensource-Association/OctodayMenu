# QQ 邮箱 SMTP 与注册验证码

后端通过 `EmailService` 支持普通文本邮件和 HTML 邮件。注册验证码邮件同时包含纯文本和 HTML 内容。

## QQ 邮箱准备

1. 登录 QQ 邮箱，在账号设置中开启 SMTP 服务。
2. 按 QQ 邮箱提示生成 16 位授权码。
3. 授权码只用于 SMTP 登录，不是 QQ 登录密码。
4. 将配置写入本地 `backend/.env` 或部署平台的环境变量，不要提交到 Git。

## 环境变量

QQ 邮箱推荐使用 465 端口和 SSL：

```env
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_SECURE=true
SMTP_USER=your_email@qq.com
SMTP_PASS=your_16_character_authorization_code
MAIL_FROM=your_email@qq.com
```

也可以使用 587 端口和 STARTTLS：

```env
SMTP_HOST=smtp.qq.com
SMTP_PORT=587
SMTP_SECURE=false
SMTP_USER=your_email@qq.com
SMTP_PASS=your_16_character_authorization_code
MAIL_FROM=your_email@qq.com
```

修改环境变量后需要重启 FastAPI 后端。

## 验证码规则

- 验证码为 6 位数字。
- 验证码有效期固定为 5 分钟。
- 同一邮箱 1 分钟内最多发送一次。
- 同一邮箱滚动 1 小时内最多发送 5 次。
- 验证码只以密码哈希形式保存。
- 发送成功的验证码才能用于注册。

`POST /api/auth/email-verifications` 在正常发送后返回：

```json
{
  "status": "sent"
}
```

只有 `ENVIRONMENT=test` 会跳过真实 SMTP 并返回 `dev_code`。development 和 production 环境未配置 SMTP 或发送失败时返回通用 `503`，不会返回验证码、授权码或 SMTP 底层错误。

## 安全要求

- 不要把真实 `SMTP_PASS` 写入 `.env.example`、README、测试、日志或前端代码。
- 不要使用 QQ 登录密码作为 `SMTP_PASS`。
- 授权码泄露后应立即在 QQ 邮箱后台撤销并重新生成。
