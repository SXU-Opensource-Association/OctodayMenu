from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.core.security import hash_password
from app.models import EmailDeliveryStatus, EmailVerification
from app.services.email import EmailDeliveryError
from app.services.email_verification import (
    EmailRateLimitError,
    consume_email_code,
    generate_code,
    send_email_code,
)


class RecordingEmailService:
    def __init__(self):
        self.calls = []

    def send_html(self, to, subject, html, text=None):
        self.calls.append(
            {
                "to": to,
                "subject": subject,
                "html": html,
                "text": text,
            }
        )


class FailingEmailService:
    def send_html(self, to, subject, html, text=None):
        raise EmailDeliveryError()


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with session_factory() as session:
        yield session


def test_only_sent_verification_codes_can_be_consumed(db):
    code = "123456"
    verification = EmailVerification(
        email="student@example.com",
        code_hash=hash_password(code),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        delivery_status=EmailDeliveryStatus.PENDING,
    )
    db.add(verification)
    db.commit()

    with pytest.raises(HTTPException):
        consume_email_code(db, verification.email, code)

    verification.delivery_status = EmailDeliveryStatus.FAILED
    db.commit()
    with pytest.raises(HTTPException):
        consume_email_code(db, verification.email, code)

    verification.delivery_status = EmailDeliveryStatus.SENT
    db.commit()
    consume_email_code(db, verification.email, code)
    db.refresh(verification)

    assert verification.consumed_at is not None


def test_generate_code_always_returns_six_digits():
    for _ in range(100):
        code = generate_code()
        assert len(code) == 6
        assert code.isdigit()


def test_test_environment_code_expires_in_exactly_five_minutes(db, monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "test")
    now = datetime(2026, 6, 27, 10, 0, tzinfo=timezone.utc)

    code = send_email_code(db, "student@example.com", now=now)
    verification = db.query(EmailVerification).one()
    expires_at = verification.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    assert code is not None
    assert expires_at == now + timedelta(minutes=5)
    assert verification.delivery_status == EmailDeliveryStatus.SENT


def test_same_email_cannot_request_twice_within_one_minute(db, monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "test")
    now = datetime(2026, 6, 27, 10, 0, tzinfo=timezone.utc)
    send_email_code(db, "student@example.com", now=now)

    with pytest.raises(EmailRateLimitError) as caught:
        send_email_code(db, "student@example.com", now=now + timedelta(seconds=59))

    assert caught.value.retry_after_seconds == 1
    assert str(caught.value) == "同一邮箱每分钟最多发送一次验证码"


def test_same_email_cannot_request_more_than_five_times_per_hour(db, monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "test")
    now = datetime(2026, 6, 27, 10, 0, tzinfo=timezone.utc)
    for minutes in (0, 12, 24, 36, 48):
        send_email_code(db, "student@example.com", now=now + timedelta(minutes=minutes))

    with pytest.raises(EmailRateLimitError) as caught:
        send_email_code(db, "student@example.com", now=now + timedelta(minutes=59))

    assert caught.value.retry_after_seconds == 60
    assert str(caught.value) == "同一邮箱每小时最多发送五次验证码"


def test_successful_smtp_delivery_marks_code_sent(db, monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "development")
    email_service = RecordingEmailService()
    now = datetime(2026, 6, 27, 10, 0, tzinfo=timezone.utc)

    returned_code = send_email_code(
        db,
        "student@example.com",
        now=now,
        email_service=email_service,
    )
    verification = db.query(EmailVerification).one()

    assert returned_code is None
    assert verification.delivery_status == EmailDeliveryStatus.SENT
    assert len(email_service.calls) == 1
    assert email_service.calls[0]["to"] == "student@example.com"
    assert "5 分钟" in email_service.calls[0]["text"]
    assert "5 分钟" in email_service.calls[0]["html"]


def test_failed_smtp_delivery_marks_code_failed(db, monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "development")
    now = datetime(2026, 6, 27, 10, 0, tzinfo=timezone.utc)

    with pytest.raises(EmailDeliveryError):
        send_email_code(
            db,
            "student@example.com",
            now=now,
            email_service=FailingEmailService(),
        )

    verification = db.query(EmailVerification).one()
    assert verification.delivery_status == EmailDeliveryStatus.FAILED
    with pytest.raises(HTTPException):
        consume_email_code(db, verification.email, "000000")
