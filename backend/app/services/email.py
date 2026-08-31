from __future__ import annotations

from collections.abc import Callable
from email.message import EmailMessage
import smtplib
import ssl
from typing import Any

from app.core.config import Settings, get_settings


class EmailConfigurationError(Exception):
    def __init__(self) -> None:
        super().__init__("邮件服务未配置")


class EmailDeliveryError(Exception):
    def __init__(self) -> None:
        super().__init__("邮件发送失败")


class EmailService:
    def __init__(
        self,
        settings: Settings | None = None,
        *,
        smtp_factory: Callable[..., Any] = smtplib.SMTP,
        smtp_ssl_factory: Callable[..., Any] = smtplib.SMTP_SSL,
    ) -> None:
        self.settings = settings or get_settings()
        self.smtp_factory = smtp_factory
        self.smtp_ssl_factory = smtp_ssl_factory
        if (
            not all(
                (
                    self.settings.smtp_host,
                    self.settings.smtp_user,
                    self.settings.smtp_pass,
                    self.settings.mail_from,
                )
            )
            or not isinstance(self.settings.smtp_port, int)
            or not 1 <= self.settings.smtp_port <= 65535
            or not isinstance(self.settings.smtp_secure, bool)
        ):
            raise EmailConfigurationError()
        self.ssl_context = ssl.create_default_context()

    def send_text(self, to: str, subject: str, text: str) -> None:
        message = self._build_message(to, subject)
        message.set_content(text)
        self._send(message)

    def send_html(self, to: str, subject: str, html: str, text: str | None = None) -> None:
        message = self._build_message(to, subject)
        message.set_content(text or "请使用支持 HTML 的邮件客户端查看此邮件。")
        message.add_alternative(html, subtype="html")
        self._send(message)

    def _build_message(self, to: str, subject: str) -> EmailMessage:
        message = EmailMessage()
        message["From"] = self.settings.mail_from
        message["To"] = to
        message["Subject"] = subject
        return message

    def _send(self, message: EmailMessage) -> None:
        try:
            if self.settings.smtp_secure:
                smtp_context = self.smtp_ssl_factory(
                    self.settings.smtp_host,
                    self.settings.smtp_port,
                    timeout=10,
                    context=self.ssl_context,
                )
            else:
                smtp_context = self.smtp_factory(
                    self.settings.smtp_host,
                    self.settings.smtp_port,
                    timeout=10,
                )
            with smtp_context as smtp:
                if not self.settings.smtp_secure:
                    smtp.starttls(context=self.ssl_context)
                smtp.login(self.settings.smtp_user, self.settings.smtp_pass)
                smtp.send_message(message)
        except Exception as exc:
            raise EmailDeliveryError() from exc
