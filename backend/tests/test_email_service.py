from email.message import EmailMessage

import pytest

from app.core.config import Settings
from app.services.email import EmailConfigurationError, EmailDeliveryError, EmailService


class FakeSMTP:
    instances = []
    send_error = None

    def __init__(self, host, port, timeout, context=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.context = context
        self.started_tls = False
        self.starttls_context = None
        self.login_args = None
        self.message = None
        type(self).instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def starttls(self, context=None):
        self.started_tls = True
        self.starttls_context = context

    def login(self, username, password):
        self.login_args = (username, password)

    def send_message(self, message):
        if type(self).send_error is not None:
            raise type(self).send_error
        self.message = message


class FakeSMTPSSL(FakeSMTP):
    instances = []


@pytest.fixture(autouse=True)
def reset_fake_smtp():
    FakeSMTP.instances = []
    FakeSMTPSSL.instances = []
    FakeSMTP.send_error = None
    FakeSMTPSSL.send_error = None


@pytest.fixture()
def smtp_environment(monkeypatch):
    values = {
        "SMTP_HOST": "smtp.qq.com",
        "SMTP_PORT": "465",
        "SMTP_SECURE": "true",
        "SMTP_USER": "sender@qq.com",
        "SMTP_PASS": "sixteen-char-code",
        "MAIL_FROM": "SXUWhatEat <sender@qq.com>",
    }
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    return values


def build_service(settings):
    return EmailService(
        settings,
        smtp_factory=FakeSMTP,
        smtp_ssl_factory=FakeSMTPSSL,
    )


def test_settings_read_exact_smtp_environment_variables(smtp_environment):
    settings = Settings()

    assert settings.smtp_host == smtp_environment["SMTP_HOST"]
    assert settings.smtp_port == 465
    assert settings.smtp_secure is True
    assert settings.smtp_user == smtp_environment["SMTP_USER"]
    assert settings.smtp_pass == smtp_environment["SMTP_PASS"]
    assert settings.mail_from == smtp_environment["MAIL_FROM"]


def test_send_text_uses_ssl_and_builds_plain_email(smtp_environment):
    service = build_service(Settings())

    service.send_text("student@example.com", "测试主题", "这是一封普通邮件。")

    assert FakeSMTP.instances == []
    assert len(FakeSMTPSSL.instances) == 1
    connection = FakeSMTPSSL.instances[0]
    assert (connection.host, connection.port, connection.timeout) == ("smtp.qq.com", 465, 10)
    assert connection.context is not None
    assert connection.started_tls is False
    assert connection.login_args == ("sender@qq.com", "sixteen-char-code")
    assert isinstance(connection.message, EmailMessage)
    assert connection.message["From"] == "SXUWhatEat <sender@qq.com>"
    assert connection.message["To"] == "student@example.com"
    assert connection.message["Subject"] == "测试主题"
    assert connection.message.get_content().strip() == "这是一封普通邮件。"
    assert "sixteen-char-code" not in connection.message.as_string()


def test_send_html_uses_starttls_and_multipart_alternative(smtp_environment, monkeypatch):
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_SECURE", "false")
    service = build_service(Settings())

    service.send_html(
        "student@example.com",
        "HTML 测试",
        "<strong>验证码 123456</strong>",
        "验证码 123456",
    )

    assert FakeSMTPSSL.instances == []
    assert len(FakeSMTP.instances) == 1
    connection = FakeSMTP.instances[0]
    assert connection.context is None
    assert connection.started_tls is True
    assert connection.starttls_context is not None
    assert connection.login_args == ("sender@qq.com", "sixteen-char-code")
    assert connection.message.is_multipart()
    contents = {part.get_content_type(): part.get_content().strip() for part in connection.message.iter_parts()}
    assert contents["text/plain"] == "验证码 123456"
    assert contents["text/html"] == "<strong>验证码 123456</strong>"


def test_missing_configuration_raises_safe_error(monkeypatch):
    for key in ("SMTP_HOST", "SMTP_USER", "SMTP_PASS", "MAIL_FROM"):
        monkeypatch.delenv(key, raising=False)

    with pytest.raises(EmailConfigurationError) as caught:
        EmailService(Settings())

    assert str(caught.value) == "邮件服务未配置"


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("SMTP_PORT", "not-a-port"),
        ("SMTP_PORT", "70000"),
        ("SMTP_SECURE", "sometimes"),
    ],
)
def test_invalid_transport_configuration_raises_safe_error(smtp_environment, monkeypatch, key, value):
    monkeypatch.setenv(key, value)

    with pytest.raises(EmailConfigurationError) as caught:
        EmailService(Settings())

    assert str(caught.value) == "邮件服务未配置"


def test_transport_failure_raises_safe_error_without_credentials(smtp_environment):
    FakeSMTPSSL.send_error = RuntimeError("sixteen-char-code leaked by transport")
    service = build_service(Settings())

    with pytest.raises(EmailDeliveryError) as caught:
        service.send_text("student@example.com", "测试", "正文")

    assert str(caught.value) == "邮件发送失败"
    assert smtp_environment["SMTP_PASS"] not in str(caught.value)
