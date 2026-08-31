# Email Service Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Add environment-configured QQ SMTP text/HTML sending and a secure, database-limited five-minute registration verification-code flow.

**Architecture:** `EmailService` owns SMTP message construction and transport while `email_verification` owns code generation, persistence, delivery status, throttling, and consumption. The auth API maps domain failures to generic HTTP errors, and only the test environment bypasses SMTP and exposes `dev_code`.

**Tech Stack:** Python 3, FastAPI, SQLAlchemy, Alembic, standard-library `email`/`smtplib`, pytest.

---

### Task 1: SMTP Configuration and EmailService

**Files:**
- Create: `backend/app/services/email.py`
- Modify: `backend/app/core/config.py`
- Test: `backend/tests/test_email_service.py`

- [x] **Step 1: Write failing configuration and text-email tests**

Create tests that set only `SMTP_HOST`, `SMTP_PORT`, `SMTP_SECURE`, `SMTP_USER`, `SMTP_PASS`, and `MAIL_FROM`, then assert `Settings` exposes those values. Add a fake SMTP context manager and assert `EmailService.send_text()` sends an `EmailMessage` with the expected sender, recipient, subject, and plain body without exposing the password in the message.

- [x] **Step 2: Run the focused tests and verify RED**

Run: `cd backend && pytest tests/test_email_service.py -q`

Expected: FAIL because `app.services.email.EmailService` and the new settings properties do not exist.

- [x] **Step 3: Implement the minimal text-email service**

Add `EmailConfigurationError` and `EmailDeliveryError` with fixed, non-sensitive messages. Build `EmailService` from `Settings`, validate all six SMTP variables, use `smtplib.SMTP_SSL` when secure and `smtplib.SMTP` plus `starttls()` otherwise, then authenticate and send an `EmailMessage`.

- [x] **Step 4: Add failing HTML and transport-mode tests**

Assert `send_html()` creates a multipart alternative message with plain and HTML bodies. Assert secure mode uses SSL without STARTTLS and non-secure mode uses SMTP with STARTTLS.

- [x] **Step 5: Implement HTML sending and pass focused tests**

Implement `send_html(to, subject, html, text=None)` using `set_content()` and `add_alternative()`. Run: `cd backend && pytest tests/test_email_service.py -q`. Expected: all tests PASS.

### Task 2: Verification Delivery Status and Migration

**Files:**
- Modify: `backend/app/models.py`
- Create: `backend/alembic/versions/20260627_0004_email_delivery_status.py`
- Test: `backend/tests/test_email_verification.py`

- [x] **Step 1: Write a failing model-state test**

Assert a verification can be stored with `PENDING`, transitioned to `SENT` or `FAILED`, and only `SENT` is considered consumable by the service API.

- [x] **Step 2: Run the focused test and verify RED**

Run: `cd backend && pytest tests/test_email_verification.py -q`

Expected: FAIL because `EmailDeliveryStatus` and `delivery_status` do not exist.

- [x] **Step 3: Add the enum, model field, and Alembic migration**

Define string enum values `PENDING`, `SENT`, and `FAILED`. Add a non-null `delivery_status` column defaulting to `PENDING`; migration `0004` adds the matching database enum/column with existing rows marked `SENT`.

- [x] **Step 4: Run the focused model test**

Run: `cd backend && pytest tests/test_email_verification.py -q`. Expected: model-state test PASS.

### Task 3: Six-Digit Code, Five-Minute Expiry, and Rate Limits

**Files:**
- Modify: `backend/app/services/email_verification.py`
- Test: `backend/tests/test_email_verification.py`

- [x] **Step 1: Write failing code-format and expiry tests**

Assert repeated `generate_code()` results match `^\d{6}$`. Freeze or inject the current time and assert generated records expire exactly five minutes later.

- [x] **Step 2: Run the focused tests and verify RED**

Run: `cd backend && pytest tests/test_email_verification.py -q`

Expected: expiry test FAIL because the current implementation uses a configurable ten-minute default.

- [x] **Step 3: Implement fixed five-minute expiry**

Use a module constant `VERIFICATION_CODE_TTL = timedelta(minutes=5)` and keep only the password hash in the database.

- [x] **Step 4: Write failing minute/hour throttling tests**

Insert attempts at controlled timestamps and assert the service rejects a second attempt within 60 seconds and a sixth attempt within one hour using a dedicated `EmailRateLimitError`.

- [x] **Step 5: Implement database-backed throttling**

Query the latest attempt and one-hour count for the normalized email before creating a new `PENDING` row. Use fixed non-sensitive messages and expose the applicable retry interval from the domain error.

- [x] **Step 6: Run focused tests**

Run: `cd backend && pytest tests/test_email_verification.py -q`. Expected: all format, expiry, and limit tests PASS.

### Task 4: SMTP Delivery and Secure API Errors

**Files:**
- Modify: `backend/app/services/email_verification.py`
- Modify: `backend/app/api/auth.py`
- Modify: `backend/app/schemas.py`
- Test: `backend/tests/test_email_verification.py`
- Test: `backend/tests/test_api.py`

- [x] **Step 1: Write failing delivery-state tests**

Inject a fake successful `EmailService` and assert the record becomes `SENT`. Inject a service raising `EmailDeliveryError` and assert the record becomes `FAILED`, the code cannot be consumed, and the exception exposed to the API contains no SMTP credential.

- [x] **Step 2: Implement HTML verification delivery**

Create a concise Chinese HTML message with a plain-text fallback. Mark the row `SENT` only after successful delivery; on a domain delivery failure mark it `FAILED` and re-raise the safe exception.

- [x] **Step 3: Write failing environment and API tests**

Assert `ENVIRONMENT=test` skips SMTP and returns `dev_code`. Assert development/production without SMTP returns generic `503` and no code. Assert delivery failure returns generic `503`; assert limit failures return `429`.

- [x] **Step 4: Implement environment boundary and HTTP mapping**

In test only, mark the record `SENT` without SMTP and return the code. In all other environments instantiate `EmailService`; map configuration/delivery errors to `503` with `邮件服务暂不可用`, and rate-limit errors to `429` without returning internal exception details.

- [x] **Step 5: Run focused API and service tests**

Run: `cd backend && pytest tests/test_email_service.py tests/test_email_verification.py tests/test_api.py -q`. Expected: all tests PASS.

### Task 5: Examples, Documentation, and Local QQ SMTP Validation

**Files:**
- Modify: `backend/.env.example`
- Modify: `docs/email-verification.md`
- Modify locally without staging: `backend/.env`

- [x] **Step 1: Update safe environment examples**

Replace legacy SMTP names with exactly:

```env
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_SECURE=true
SMTP_USER=your_email@qq.com
SMTP_PASS=your_16_character_authorization_code
MAIL_FROM=your_email@qq.com
```

Do not include real credentials.

- [x] **Step 2: Update operator documentation**

Document QQ SMTP enablement, the distinction between authorization code and login password, SSL 465 defaults, test-only `dev_code`, rate limits, and restart requirements.

- [x] **Step 3: Create a local untracked SMTP configuration**

Write the user-provided QQ address and authorization code to `backend/.env`, verify `.gitignore` excludes it, and never print the file contents.

- [x] **Step 4: Run the migration verification**

Create a temporary SQLite database and run `alembic upgrade head`. Expected: revisions `0001` through `0004` apply successfully.

- [x] **Step 5: Run full automated verification**

Run: `cd backend && pytest -q`. Expected: zero failures.

- [x] **Step 6: Run a real QQ SMTP smoke test**

With `ENVIRONMENT=development`, invoke `EmailService.send_text()` to send a harmless test message to the configured sender mailbox. Report only success/failure and never print credentials or raw SMTP exception details.

- [x] **Step 7: Inspect the final diff for secrets**

Run secret-oriented searches over tracked/untracked source files while excluding `backend/.env`, and confirm the real mailbox and authorization code are absent from staged or committed content.
