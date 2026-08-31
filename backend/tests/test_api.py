import os
from datetime import date
from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.core.deps import get_db
from app.core.security import verify_password
from app.main import create_app
from app.models import AreaType, DailyDraw, Dish, FoodArea, FoodVendor, User
from app.services.dev_seed import seed_development_data
from app.services.email import EmailDeliveryError
from app.services.seed import ensure_super_admin


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("SUPER_ADMIN_EMAIL", "root@example.com")
    monkeypatch.setenv("SUPER_ADMIN_PASSWORD", "RootPassword123")

    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    app = create_app(run_startup=False)
    app.state.session_factory = TestingSessionLocal

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestingSessionLocal() as db:
        ensure_super_admin(db)
    with TestClient(app) as test_client:
        test_client.session_factory = TestingSessionLocal
        yield test_client


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def register_and_login(client, email="student@example.com", password="StudentPass123"):
    code_response = client.post("/api/auth/email-verifications", json={"email": email})
    assert code_response.status_code == 201
    verification_code = code_response.json()["dev_code"]
    response = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": password,
            "display_name": "学生",
            "verification_code": verification_code,
        },
    )
    assert response.status_code == 201
    token = response.json()["access_token"]
    return token


def login(client, email, password):
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    if response.status_code == 202:
        response = client.post(
            "/api/auth/login",
            json={
                "email": email,
                "password": password,
                "verification_code": response.json()["dev_code"],
            },
        )
    assert response.status_code == 200
    return response.json()["access_token"]


def create_restaurant_tree(client, admin_token):
    headers = auth_headers(admin_token)
    restaurant = client.post(
        "/api/admin/restaurants",
        headers=headers,
        json={"name": "文瀛餐厅", "description": "主校区热门餐厅", "address": "南区"},
    )
    assert restaurant.status_code == 201
    restaurant_id = restaurant.json()["id"]

    floor = client.post(
        f"/api/admin/restaurants/{restaurant_id}/floors",
        headers=headers,
        json={"name": "一层", "level": 1, "description": "快餐和面食"},
    )
    assert floor.status_code == 201
    floor_id = floor.json()["id"]

    stall = client.post(
        f"/api/admin/floors/{floor_id}/stalls",
        headers=headers,
        json={"name": "山西面馆", "description": "刀削面和拌面", "location_hint": "东侧"},
    )
    assert stall.status_code == 201
    stall_id = stall.json()["id"]

    basic_tag = client.post(
        "/api/admin/tags",
        headers=headers,
        json={"name": "面", "category": "basic"},
    )
    assert basic_tag.status_code == 201
    taste_tag = client.post(
        "/api/admin/tags",
        headers=headers,
        json={"name": "辣", "category": "taste"},
    )
    assert taste_tag.status_code == 201

    dish = client.post(
        f"/api/admin/stalls/{stall_id}/dishes",
        headers=headers,
        json={
            "name": "油泼刀削面",
            "description": "香辣筋道",
            "price": "12.50",
            "image_url": "https://example.com/noodles.jpg",
            "tag_ids": [basic_tag.json()["id"], taste_tag.json()["id"]],
        },
    )
    assert dish.status_code == 201
    return {
        "restaurant_id": restaurant_id,
        "floor_id": floor_id,
        "stall_id": stall_id,
        "dish_id": dish.json()["id"],
        "basic_tag_id": basic_tag.json()["id"],
        "taste_tag_id": taste_tag.json()["id"],
    }


def create_food_area_dish(client, admin_token, area_type="SNACK_STREET", area_name="许西小吃街", vendor_name="东北饺子馆"):
    headers = auth_headers(admin_token)
    area = client.post(
        "/api/admin/food-areas",
        headers=headers,
        json={"name": area_name, "area_type": area_type, "location": "校门外东侧", "description": "测试地点"},
    )
    assert area.status_code == 201
    area_id = area.json()["id"]

    section_id = None
    if area_type == "CANTEEN":
        section = client.post(
            f"/api/admin/food-areas/{area_id}/sections",
            headers=headers,
            json={"name": "一层", "level": 1, "description": "餐厅楼层"},
        )
        assert section.status_code == 201
        section_id = section.json()["id"]
        vendor_url = f"/api/admin/sections/{section_id}/vendors"
    else:
        vendor_url = f"/api/admin/food-areas/{area_id}/vendors"

    vendor = client.post(
        vendor_url,
        headers=headers,
        json={"name": vendor_name, "description": "测试店铺", "location_hint": "路口第一家"},
    )
    assert vendor.status_code == 201
    vendor_id = vendor.json()["id"]

    dish = client.post(
        f"/api/admin/vendors/{vendor_id}/dishes",
        headers=headers,
        json={"name": "招牌水饺", "description": "手工现包", "price": "15.00", "tag_ids": []},
    )
    assert dish.status_code == 201
    return {"area_id": area_id, "section_id": section_id, "vendor_id": vendor_id, "dish_id": dish.json()["id"]}


def build_import_workbook(rows):
    from openpyxl import Workbook

    headers = [
        "类型",
        "地点名称",
        "大概位置",
        "楼层名称",
        "楼层序号",
        "店铺/窗口名称",
        "店铺位置",
        "菜品名称",
        "价格",
        "基础标签",
        "味道标签",
        "菜品简介",
        "图片URL",
        "是否启用",
        "是否供应",
    ]
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "food-data"
    sheet.append(headers)
    for row in rows:
        sheet.append([row.get(header) for header in headers])
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return buffer


def test_super_admin_seed_and_password_login(client):
    token = login(client, "root@example.com", "RootPassword123")
    response = client.get("/api/auth/me", headers=auth_headers(token))

    assert response.status_code == 200
    assert response.json()["email"] == "root@example.com"
    assert response.json()["role"] == "SUPER_ADMIN"

    with client.session_factory() as db:
        user = db.query(User).filter(User.email == "root@example.com").one()
        assert user.password_hash != "RootPassword123"
        assert user.password_hash.startswith("pbkdf2_sha256$")


def test_super_admin_seed_does_not_reset_existing_password(client, monkeypatch):
    monkeypatch.setenv("SUPER_ADMIN_EMAIL", "root@example.com")
    monkeypatch.setenv("SUPER_ADMIN_PASSWORD", "NewRootPassword123")

    with client.session_factory() as db:
        user = ensure_super_admin(db)
        assert user is not None
        assert verify_password("RootPassword123", user.password_hash)
        assert not verify_password("NewRootPassword123", user.password_hash)


def test_dev_seed_merges_partial_data_idempotently(client):
    with client.session_factory() as db:
        db.add(
            FoodArea(
                area_type=AreaType.CANTEEN,
                name="文瀛餐厅",
                description="已有但未录入窗口的地点",
                location="南区",
            )
        )
        db.commit()

        seed_development_data(db)
        first_counts = (
            db.query(FoodArea).count(),
            db.query(FoodVendor).count(),
            db.query(Dish).count(),
        )
        seed_development_data(db)
        second_counts = (
            db.query(FoodArea).count(),
            db.query(FoodVendor).count(),
            db.query(Dish).count(),
        )

        assert {area.area_type for area in db.query(FoodArea).all()} == {
            AreaType.CANTEEN,
            AreaType.SNACK_STREET,
            AreaType.CUSTOM_AREA,
        }
        assert first_counts == second_counts
        assert first_counts[1] >= 5
        assert first_counts[2] >= 12
        assert db.query(Dish).filter(Dish.is_available.is_(True)).count() >= 12


def test_user_register_login_and_me(client):
    token = register_and_login(client)
    response = client.get("/api/auth/me", headers=auth_headers(token))

    assert response.status_code == 200
    assert response.json()["email"] == "student@example.com"
    assert response.json()["role"] == "USER"

    bad_login = client.post(
        "/api/auth/login",
        json={"email": "student@example.com", "password": "wrong-password"},
    )
    assert bad_login.status_code == 401


def test_register_requires_email_verification_code(client):
    rejected = client.post(
        "/api/auth/register",
        json={
            "email": "verify@example.com",
            "password": "StudentPass123",
            "display_name": "验证学生",
            "verification_code": "000000",
        },
    )
    assert rejected.status_code == 400
    assert rejected.json()["detail"] == "邮箱验证码无效或已过期"

    sent = client.post("/api/auth/email-verifications", json={"email": "verify@example.com"})
    assert sent.status_code == 201
    assert len(sent.json()["dev_code"]) == 6

    created = client.post(
        "/api/auth/register",
        json={
            "email": "verify@example.com",
            "password": "StudentPass123",
            "display_name": "验证学生",
            "verification_code": sent.json()["dev_code"],
        },
    )
    assert created.status_code == 201
    assert created.json()["user"]["email"] == "verify@example.com"

    reused = client.post(
        "/api/auth/register",
        json={
            "email": "another@example.com",
            "password": "StudentPass123",
            "display_name": "复用验证码",
            "verification_code": sent.json()["dev_code"],
        },
    )
    assert reused.status_code == 400


def test_email_verification_rate_limit_returns_429(client):
    first = client.post("/api/auth/email-verifications", json={"email": "limited@example.com"})
    second = client.post("/api/auth/email-verifications", json={"email": "limited@example.com"})

    assert first.status_code == 201
    assert second.status_code == 429
    assert second.json()["detail"] == "同一邮箱每分钟最多发送一次验证码"
    assert int(second.headers["Retry-After"]) > 0


@pytest.mark.parametrize("environment", ["development", "production"])
def test_non_test_environment_without_smtp_returns_safe_503(client, monkeypatch, environment):
    monkeypatch.setenv("ENVIRONMENT", environment)
    monkeypatch.setenv("SECRET_KEY", "production-test-secret-key-at-least-32-characters")
    for key in ("SMTP_HOST", "SMTP_USER", "SMTP_PASS", "MAIL_FROM"):
        monkeypatch.delenv(key, raising=False)

    response = client.post(
        "/api/auth/email-verifications",
        json={"email": f"{environment}@example.com"},
    )

    assert response.status_code == 503
    assert response.json() == {"detail": "邮件服务暂不可用"}
    assert "dev_code" not in response.text


def test_smtp_failure_returns_safe_503_without_transport_details(client, monkeypatch):
    class FailingEmailService:
        def __init__(self, settings):
            pass

        def send_html(self, to, subject, html, text=None):
            raise EmailDeliveryError()

    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setattr("app.services.email_verification.EmailService", FailingEmailService)

    response = client.post(
        "/api/auth/email-verifications",
        json={"email": "failure@example.com"},
    )

    assert response.status_code == 503
    assert response.json() == {"detail": "邮件服务暂不可用"}
    assert "SMTP_PASS" not in response.text
    assert "authorization" not in response.text.lower()


def test_development_smtp_success_does_not_return_dev_code(client, monkeypatch):
    class SuccessfulEmailService:
        def __init__(self, settings):
            pass

        def send_html(self, to, subject, html, text=None):
            return None

    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setattr("app.services.email_verification.EmailService", SuccessfulEmailService)

    response = client.post(
        "/api/auth/email-verifications",
        json={"email": "delivered@example.com"},
    )

    assert response.status_code == 201
    assert response.json() == {"status": "sent"}


def test_admin_can_manage_restaurant_tree_and_public_can_browse(client):
    admin_token = login(client, "root@example.com", "RootPassword123")
    created = create_restaurant_tree(client, admin_token)

    restaurants = client.get("/api/restaurants")
    assert restaurants.status_code == 200
    assert restaurants.json()[0]["name"] == "文瀛餐厅"

    detail = client.get(f"/api/restaurants/{created['restaurant_id']}")
    assert detail.status_code == 200
    data = detail.json()
    assert data["floors"][0]["stalls"][0]["dishes"][0]["name"] == "油泼刀削面"
    assert data["floors"][0]["stalls"][0]["like_count"] == 0
    assert data["floors"][0]["stalls"][0]["comment_count"] == 0

    dishes = client.get(f"/api/dishes?tag_ids={created['taste_tag_id']}")
    assert dishes.status_code == 200
    assert [dish["name"] for dish in dishes.json()] == ["油泼刀削面"]


def test_admin_can_manage_three_food_area_types_and_public_can_browse(client):
    admin_token = login(client, "root@example.com", "RootPassword123")
    headers = auth_headers(admin_token)

    canteen = create_food_area_dish(
        client,
        admin_token,
        area_type="CANTEEN",
        area_name="文瀛餐厅",
        vendor_name="山西面馆",
    )
    snack = create_food_area_dish(client, admin_token)
    custom = create_food_area_dish(
        client,
        admin_token,
        area_type="CUSTOM_AREA",
        area_name="实验楼旁",
        vendor_name="咖啡简餐",
    )

    areas = client.get("/api/food-areas")
    assert areas.status_code == 200
    assert {area["area_type"] for area in areas.json()} == {"CANTEEN", "SNACK_STREET", "CUSTOM_AREA"}

    canteen_detail = client.get(f"/api/food-areas/{canteen['area_id']}")
    assert canteen_detail.status_code == 200
    assert canteen_detail.json()["sections"][0]["vendors"][0]["dishes"][0]["name"] == "招牌水饺"

    snack_detail = client.get(f"/api/food-areas/{snack['area_id']}")
    assert snack_detail.status_code == 200
    assert snack_detail.json()["sections"] == []
    assert snack_detail.json()["vendors"][0]["name"] == "东北饺子馆"

    custom_dishes = client.get("/api/dishes?area_type=CUSTOM_AREA")
    assert custom_dishes.status_code == 200
    assert [dish["id"] for dish in custom_dishes.json()] == [custom["dish_id"]]

    rejected = client.post(
        f"/api/admin/food-areas/{canteen['area_id']}/vendors",
        headers=headers,
        json={"name": "无楼层窗口"},
    )
    assert rejected.status_code == 400

    compatible = client.get("/api/restaurants")
    assert compatible.status_code == 200
    assert [area["name"] for area in compatible.json()] == ["文瀛餐厅"]


def test_basic_admin_can_manage_content_but_not_admins(client):
    super_token = login(client, "root@example.com", "RootPassword123")
    create_admin = client.post(
        "/api/admin/admins",
        headers=auth_headers(super_token),
        json={"email": "ops@example.com", "password": "OpsPassword123", "display_name": "运营"},
    )
    assert create_admin.status_code == 201
    admin_token = login(client, "ops@example.com", "OpsPassword123")

    visible_admins = client.get("/api/admin/admins", headers=auth_headers(admin_token))
    assert visible_admins.status_code == 200
    assert {item["email"] for item in visible_admins.json()} == {"root@example.com", "ops@example.com"}

    restaurant = client.post(
        "/api/admin/restaurants",
        headers=auth_headers(admin_token),
        json={"name": "令德餐厅"},
    )
    assert restaurant.status_code == 201

    forbidden = client.post(
        "/api/admin/admins",
        headers=auth_headers(admin_token),
        json={"email": "another@example.com", "password": "AnotherPass123"},
    )
    assert forbidden.status_code == 403


def test_basic_admin_can_crud_snack_street_location(client):
    super_token = login(client, "root@example.com", "RootPassword123")
    client.post(
        "/api/admin/admins",
        headers=auth_headers(super_token),
        json={"email": "location-admin@example.com", "password": "LocationAdmin123"},
    )
    admin_token = login(client, "location-admin@example.com", "LocationAdmin123")
    headers = auth_headers(admin_token)

    created = client.post(
        "/api/admin/food-areas",
        headers=headers,
        json={
            "name": "山西大学西侧小吃街",
            "area_type": "SNACK_STREET",
            "location": "山西大学西门外",
            "description": "校边小吃集中区域",
        },
    )
    assert created.status_code == 201
    area_id = created.json()["id"]

    listed = client.get("/api/admin/food-areas", headers=headers)
    assert any(area["id"] == area_id for area in listed.json())

    updated = client.patch(
        f"/api/admin/food-areas/{area_id}",
        headers=headers,
        json={"location": "山西大学西门北侧"},
    )
    assert updated.status_code == 200
    assert updated.json()["location"] == "山西大学西门北侧"

    deleted = client.delete(f"/api/admin/food-areas/{area_id}", headers=headers)
    assert deleted.status_code == 200


def test_admin_can_mute_blacklist_and_restore_regular_user(client):
    user_token = register_and_login(client, email="moderated-user@example.com")
    admin_token = login(client, "root@example.com", "RootPassword123")
    admin_headers = auth_headers(admin_token)
    user_headers = auth_headers(user_token)
    food = create_food_area_dish(client, admin_token)

    users = client.get("/api/admin/users", headers=admin_headers)
    target = next(user for user in users.json() if user["email"] == "moderated-user@example.com")
    assert target["is_blacklisted"] is False
    assert target["is_muted"] is False

    muted = client.post(f"/api/admin/users/{target['id']}/mute", headers=admin_headers)
    assert muted.status_code == 200
    assert muted.json()["is_muted"] is True

    like = client.post(f"/api/vendors/{food['vendor_id']}/like", headers=user_headers)
    assert like.status_code == 200
    blocked_comment = client.post(
        f"/api/vendors/{food['vendor_id']}/comments",
        headers=user_headers,
        json={"content": "这条评论不应被发布"},
    )
    assert blocked_comment.status_code == 403
    assert blocked_comment.json()["detail"] == "账号已被禁言"

    unmuted = client.delete(f"/api/admin/users/{target['id']}/mute", headers=admin_headers)
    assert unmuted.status_code == 200
    assert unmuted.json()["is_muted"] is False
    allowed_comment = client.post(
        f"/api/vendors/{food['vendor_id']}/comments",
        headers=user_headers,
        json={"content": "解除禁言后可以发布"},
    )
    assert allowed_comment.status_code == 201

    blacklisted = client.post(f"/api/admin/users/{target['id']}/blacklist", headers=admin_headers)
    assert blacklisted.status_code == 200
    assert blacklisted.json()["is_blacklisted"] is True
    assert client.get("/api/auth/me", headers=user_headers).status_code == 401
    rejected_login = client.post(
        "/api/auth/login",
        json={"email": "moderated-user@example.com", "password": "StudentPass123"},
    )
    assert rejected_login.status_code == 403
    assert rejected_login.json()["detail"] == "账号已被列入黑名单"

    restored = client.delete(f"/api/admin/users/{target['id']}/blacklist", headers=admin_headers)
    assert restored.status_code == 200
    assert restored.json()["is_blacklisted"] is False
    assert login(client, "moderated-user@example.com", "StudentPass123")


def test_admin_can_publish_list_and_delete_announcements(client):
    admin_token = login(client, "root@example.com", "RootPassword123")
    headers = auth_headers(admin_token)

    info = client.post(
        "/api/admin/announcements",
        headers=headers,
        json={"title": "本周菜单更新", "content": "新增校西小吃街店铺。", "level": "INFO"},
    )
    assert info.status_code == 201
    important = client.post(
        "/api/admin/announcements",
        headers=headers,
        json={"title": "系统维护", "content": "今晚 23:00 进行短时维护。", "level": "IMPORTANT"},
    )
    assert important.status_code == 201
    expired = client.post(
        "/api/admin/announcements",
        headers=headers,
        json={
            "title": "过期公告",
            "content": "不应出现在用户端。",
            "level": "INFO",
            "expires_at": "2000-01-01T00:00:00Z",
        },
    )
    assert expired.status_code == 201

    admin_list = client.get("/api/admin/announcements", headers=headers)
    assert admin_list.status_code == 200
    assert len(admin_list.json()) == 3

    public_list = client.get("/api/announcements")
    assert public_list.status_code == 200
    assert [item["title"] for item in public_list.json()] == ["系统维护", "本周菜单更新"]

    deleted = client.delete(f"/api/admin/announcements/{important.json()['id']}", headers=headers)
    assert deleted.status_code == 200
    assert [item["title"] for item in client.get("/api/announcements").json()] == ["本周菜单更新"]


def test_browser_auth_uses_http_only_cookie_and_logout_clears_it(client):
    token = register_and_login(client)

    authenticated = client.get("/api/auth/me")
    assert authenticated.status_code == 200
    assert authenticated.json()["email"] == "student@example.com"

    logged_out = client.post("/api/auth/logout")
    assert logged_out.status_code == 200
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers=auth_headers(token)).status_code == 401


def test_cookie_authenticated_mutations_reject_untrusted_origins(client):
    register_and_login(client)
    rejected = client.post(
        "/api/auth/logout",
        headers={"Origin": "https://evil.example"},
    )
    assert rejected.status_code == 403
    assert rejected.json()["detail"] == "请求来源不受信任"


def test_admin_login_requires_email_mfa(client):
    challenge = client.post(
        "/api/auth/login",
        json={"email": "root@example.com", "password": "RootPassword123"},
    )
    assert challenge.status_code == 202
    assert challenge.json()["mfa_required"] is True
    assert challenge.json()["dev_code"]
    assert "sxuwhateat_auth" not in challenge.cookies

    verified = client.post(
        "/api/auth/login",
        json={
            "email": "root@example.com",
            "password": "RootPassword123",
            "verification_code": challenge.json()["dev_code"],
        },
    )
    assert verified.status_code == 200
    assert verified.cookies["sxuwhateat_auth"]
    assert "HttpOnly" in verified.headers["set-cookie"]


def test_login_is_rate_limited_after_repeated_failures(client):
    for _ in range(5):
        response = client.post(
            "/api/auth/login",
            json={"email": "attacker@example.com", "password": "wrong-password"},
        )
        assert response.status_code == 401
    blocked = client.post(
        "/api/auth/login",
        json={"email": "attacker@example.com", "password": "wrong-password"},
    )
    assert blocked.status_code == 429
    assert int(blocked.headers["Retry-After"]) > 0


def test_super_admin_can_transfer_role_to_basic_admin(client):
    root_token = login(client, "root@example.com", "RootPassword123")
    created = client.post(
        "/api/admin/admins",
        headers=auth_headers(root_token),
        json={"email": "next-root@example.com", "password": "NextRootPassword123"},
    )
    assert created.status_code == 201

    transferred = client.post(
        f"/api/admin/admins/{created.json()['id']}/transfer-super-admin",
        headers=auth_headers(root_token),
    )
    assert transferred.status_code == 200
    assert transferred.json()["role"] == "SUPER_ADMIN"

    old_root = client.get("/api/auth/me", headers=auth_headers(root_token))
    assert old_root.json()["role"] == "ADMIN"
    forbidden = client.post(
        "/api/admin/admins",
        headers=auth_headers(root_token),
        json={"email": "forbidden@example.com", "password": "ForbiddenPassword123"},
    )
    assert forbidden.status_code == 403

    with client.session_factory() as db:
        seeded = ensure_super_admin(db)
        assert seeded is not None
        assert seeded.email == "next-root@example.com"


def test_admin_full_crud_is_audited(client):
    token = login(client, "root@example.com", "RootPassword123")
    headers = auth_headers(token)

    area = client.post(
        "/api/admin/food-areas",
        headers=headers,
        json={"name": "测试餐厅", "area_type": "CANTEEN", "location": "校内"},
    ).json()
    area_update = client.patch(
        f"/api/admin/food-areas/{area['id']}",
        headers=headers,
        json={"name": "测试餐厅（新）", "description": "已编辑"},
    )
    assert area_update.status_code == 200

    section = client.post(
        f"/api/admin/food-areas/{area['id']}/sections",
        headers=headers,
        json={"name": "一层", "level": 1},
    ).json()
    assert client.patch(
        f"/api/admin/sections/{section['id']}", headers=headers, json={"name": "首层"}
    ).status_code == 200

    vendor = client.post(
        f"/api/admin/sections/{section['id']}/vendors",
        headers=headers,
        json={"name": "测试窗口", "image_url": "/uploads/admin-images/test.png"},
    ).json()
    assert client.patch(
        f"/api/admin/vendors/{vendor['id']}", headers=headers, json={"location_hint": "东侧"}
    ).status_code == 200

    tag = client.post(
        "/api/admin/tags", headers=headers, json={"name": "测试标签", "category": "basic"}
    ).json()
    assert client.patch(
        f"/api/admin/tags/{tag['id']}", headers=headers, json={"name": "测试标签（新）"}
    ).status_code == 200

    dish = client.post(
        f"/api/admin/vendors/{vendor['id']}/dishes",
        headers=headers,
        json={"name": "测试菜品", "price": "10.00", "tag_ids": [tag["id"]]},
    ).json()
    assert client.patch(
        f"/api/admin/dishes/{dish['id']}",
        headers=headers,
        json={"name": "测试菜品（新）", "price": "11.00", "tag_ids": []},
    ).status_code == 200

    assert client.delete(f"/api/admin/dishes/{dish['id']}", headers=headers).status_code == 200
    assert client.delete(f"/api/admin/tags/{tag['id']}", headers=headers).status_code == 200
    assert client.delete(f"/api/admin/vendors/{vendor['id']}", headers=headers).status_code == 200
    assert client.delete(f"/api/admin/sections/{section['id']}", headers=headers).status_code == 200
    assert client.delete(f"/api/admin/food-areas/{area['id']}", headers=headers).status_code == 200

    logs = client.get("/api/admin/audit-logs", headers=headers)
    assert logs.status_code == 200
    assert len(logs.json()) >= 14
    assert {item["action"] for item in logs.json()} >= {"POST", "PATCH", "DELETE"}
    assert all("password" not in item["resource"].lower() for item in logs.json())


def test_admin_can_update_regular_users(client):
    user_token = register_and_login(client)
    super_token = login(client, "root@example.com", "RootPassword123")
    user_id = client.get("/api/auth/me", headers=auth_headers(user_token)).json()["id"]

    updated = client.patch(
        f"/api/admin/users/{user_id}",
        headers=auth_headers(super_token),
        json={"display_name": "停用学生", "is_active": False},
    )
    assert updated.status_code == 200
    assert updated.json()["display_name"] == "停用学生"
    assert updated.json()["is_active"] is False

    rejected = client.post(
        "/api/auth/login",
        json={"email": "student@example.com", "password": "StudentPass123"},
    )
    assert rejected.status_code == 403


def test_daily_draw_is_fixed_for_each_user_and_date(client):
    user_token = register_and_login(client)
    admin_token = login(client, "root@example.com", "RootPassword123")
    created = create_restaurant_tree(client, admin_token)

    first = client.post(
        "/api/draws/today",
        headers=auth_headers(user_token),
        json={"restaurant_id": created["restaurant_id"], "tag_ids": [created["taste_tag_id"]]},
    )
    assert first.status_code == 201
    assert first.json()["dish"]["id"] == created["dish_id"]

    second = client.post(
        "/api/draws/today",
        headers=auth_headers(user_token),
        json={"restaurant_id": created["restaurant_id"], "tag_ids": []},
    )
    assert second.status_code == 200
    assert second.json()["id"] == first.json()["id"]
    assert second.json()["dish"]["id"] == created["dish_id"]

    with client.session_factory() as db:
        draws = db.query(DailyDraw).filter(DailyDraw.draw_date == date.today()).all()
        assert len(draws) == 1


def test_daily_draw_ignores_filter_payload_and_uses_all_available_dishes(client):
    user_token = register_and_login(client)
    admin_token = login(client, "root@example.com", "RootPassword123")
    created = create_restaurant_tree(client, admin_token)

    response = client.post(
        "/api/draws/today",
        headers=auth_headers(user_token),
        json={"restaurant_id": 9999, "tag_ids": []},
    )

    assert response.status_code == 201
    assert response.json()["dish"]["id"] == created["dish_id"]


def test_daily_draw_uses_new_food_area_candidates(client):
    user_token = register_and_login(client)
    admin_token = login(client, "root@example.com", "RootPassword123")
    created = create_food_area_dish(client, admin_token, area_type="SNACK_STREET")

    response = client.post("/api/draws/today", headers=auth_headers(user_token), json={})

    assert response.status_code == 201
    assert response.json()["dish"]["id"] == created["dish_id"]
    assert response.json()["food_area"]["area_type"] == "SNACK_STREET"
    assert response.json()["vendor"]["name"] == "东北饺子馆"


def test_daily_draw_reports_no_candidates_when_no_available_dishes(client):
    user_token = register_and_login(client)
    response = client.post("/api/draws/today", headers=auth_headers(user_token), json={})

    assert response.status_code == 404
    assert response.json()["detail"] == "没有可抽取的菜品"


def test_super_admin_cannot_delete_last_super_admin(client):
    token = login(client, "root@example.com", "RootPassword123")
    me = client.get("/api/auth/me", headers=auth_headers(token)).json()

    response = client.delete(f"/api/admin/admins/{me['id']}", headers=auth_headers(token))

    assert response.status_code == 400
    assert response.json()["detail"] == "不能删除超级管理员，请先转让权限"


def test_admin_can_download_template_and_import_food_data_with_update_merge(client):
    admin_token = login(client, "root@example.com", "RootPassword123")
    headers = auth_headers(admin_token)

    template = client.get("/api/admin/import/food-template", headers=headers)
    assert template.status_code == 200
    assert "spreadsheet" in template.headers["content-type"]

    workbook = build_import_workbook(
        [
            {
                "类型": "小吃街",
                "地点名称": "许西小吃街",
                "大概位置": "南门外",
                "店铺/窗口名称": "东北饺子馆",
                "店铺位置": "入口左侧",
                "菜品名称": "招牌水饺",
                "价格": "15.00",
                "基础标签": "面",
                "味道标签": "鲜",
                "菜品简介": "手工现包",
                "是否启用": "是",
                "是否供应": "是",
            },
            {
                "类型": "餐厅",
                "地点名称": "文瀛餐厅",
                "大概位置": "南区",
                "楼层名称": "一层",
                "楼层序号": 1,
                "店铺/窗口名称": "山西面馆",
                "菜品名称": "油泼刀削面",
                "价格": "12.50",
                "基础标签": "面",
                "味道标签": "辣",
                "是否启用": "是",
                "是否供应": "是",
            },
        ]
    )
    dry_run = client.post(
        "/api/admin/import/food-data?dry_run=true",
        headers=headers,
        files={"file": ("food.xlsx", workbook.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert dry_run.status_code == 200
    assert dry_run.json()["dry_run"] is True
    assert dry_run.json()["created_count"] == 10
    assert dry_run.json()["error_count"] == 0
    assert client.get("/api/food-areas").json() == []

    workbook.seek(0)
    imported = client.post(
        "/api/admin/import/food-data?dry_run=false",
        headers=headers,
        files={"file": ("food.xlsx", workbook.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert imported.status_code == 200
    assert imported.json()["created_count"] == 10
    assert imported.json()["updated_count"] == 0

    update_workbook = build_import_workbook(
        [
            {
                "类型": "小吃街",
                "地点名称": "许西小吃街",
                "大概位置": "南门外",
                "店铺/窗口名称": "东北饺子馆",
                "菜品名称": "招牌水饺",
                "价格": "16.50",
                "基础标签": "面",
                "味道标签": "鲜",
                "菜品简介": "价格已更新",
                "是否启用": "是",
                "是否供应": "是",
            }
        ]
    )
    updated = client.post(
        "/api/admin/import/food-data",
        headers=headers,
        files={"file": ("food.xlsx", update_workbook.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert updated.status_code == 200
    assert updated.json()["created_count"] == 0
    assert updated.json()["updated_count"] >= 1

    dishes = client.get("/api/dishes?area_type=SNACK_STREET")
    assert dishes.status_code == 200
    assert dishes.json()[0]["price"] == "16.50"


def test_food_import_reports_row_level_errors(client):
    admin_token = login(client, "root@example.com", "RootPassword123")
    workbook = build_import_workbook(
        [
            {
                "类型": "未知类型",
                "地点名称": "错误地点",
                "店铺/窗口名称": "错误店",
                "菜品名称": "",
                "价格": "not-a-price",
            }
        ]
    )

    response = client.post(
        "/api/admin/import/food-data?dry_run=true",
        headers=auth_headers(admin_token),
        files={"file": ("food.xlsx", workbook.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )

    assert response.status_code == 400
    assert response.json()["error_count"] == 1
    assert response.json()["errors"][0]["row"] == 2


def test_social_endpoints_require_login(client):
    admin_token = login(client, "root@example.com", "RootPassword123")
    created = create_food_area_dish(client, admin_token)
    client.cookies.clear()

    like_response = client.post(f"/api/vendors/{created['vendor_id']}/like")
    comments_response = client.get(f"/api/vendors/{created['vendor_id']}/comments")
    upload_response = client.post(
        "/api/uploads/comment-images",
        files={"file": ("scene.png", b"\x89PNG\r\n\x1a\ncomment-image", "image/png")},
    )

    assert like_response.status_code == 401
    assert comments_response.status_code == 401
    assert upload_response.status_code == 401


def test_vendor_like_toggles_and_updates_count(client):
    user_token = register_and_login(client)
    admin_token = login(client, "root@example.com", "RootPassword123")
    created = create_food_area_dish(client, admin_token)
    headers = auth_headers(user_token)

    liked = client.post(f"/api/vendors/{created['vendor_id']}/like", headers=headers)
    assert liked.status_code == 200
    assert liked.json() == {"liked": True, "like_count": 1}

    detail = client.get(f"/api/food-areas/{created['area_id']}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["vendors"][0]["like_count"] == 1
    assert detail.json()["vendors"][0]["liked_by_me"] is True

    unliked = client.post(f"/api/vendors/{created['vendor_id']}/like", headers=headers)
    assert unliked.status_code == 200
    assert unliked.json() == {"liked": False, "like_count": 0}


def test_comments_replies_and_comment_likes(client):
    user_token = register_and_login(client)
    second_user_token = register_and_login(client, email="friend@example.com")
    admin_token = login(client, "root@example.com", "RootPassword123")
    created = create_food_area_dish(client, admin_token)

    comment = client.post(
        f"/api/vendors/{created['vendor_id']}/comments",
        headers=auth_headers(user_token),
        json={"content": "这家窗口排队快，口味稳定。", "image_url": "/uploads/comment-images/scene.webp"},
    )
    assert comment.status_code == 201
    comment_id = comment.json()["id"]
    assert comment.json()["author"]["display_name"] == "学生"
    assert comment.json()["image_url"] == "/uploads/comment-images/scene.webp"

    reply = client.post(
        f"/api/comments/{comment_id}/replies",
        headers=auth_headers(second_user_token),
        json={"content": "中午十二点还快吗？"},
    )
    assert reply.status_code == 201

    liked = client.post(f"/api/comments/{comment_id}/like", headers=auth_headers(second_user_token))
    assert liked.status_code == 200
    assert liked.json() == {"liked": True, "like_count": 1}

    comments = client.get(f"/api/vendors/{created['vendor_id']}/comments", headers=auth_headers(second_user_token))
    assert comments.status_code == 200
    data = comments.json()
    assert len(data) == 1
    assert data[0]["content"] == "这家窗口排队快，口味稳定。"
    assert data[0]["liked_by_me"] is True
    assert data[0]["reply_count"] == 1
    assert data[0]["replies"][0]["content"] == "中午十二点还快吗？"

    unliked = client.post(f"/api/comments/{comment_id}/like", headers=auth_headers(second_user_token))
    assert unliked.status_code == 200
    assert unliked.json() == {"liked": False, "like_count": 0}


def test_inactive_user_cannot_comment(client):
    user_token = register_and_login(client)
    admin_token = login(client, "root@example.com", "RootPassword123")
    created = create_food_area_dish(client, admin_token)
    user_id = client.get("/api/auth/me", headers=auth_headers(user_token)).json()["id"]

    stopped = client.patch(
        f"/api/admin/users/{user_id}",
        headers=auth_headers(admin_token),
        json={"is_active": False},
    )
    assert stopped.status_code == 200

    response = client.post(
        f"/api/vendors/{created['vendor_id']}/comments",
        headers=auth_headers(user_token),
        json={"content": "账号停用后不能继续发言。"},
    )

    assert response.status_code == 403


def test_comment_image_upload_validates_format_and_size(client):
    user_token = register_and_login(client)
    headers = auth_headers(user_token)

    uploaded = client.post(
        "/api/uploads/comment-images",
        headers=headers,
        files={"file": ("scene.png", b"\x89PNG\r\n\x1a\ncomment-image", "image/png")},
    )
    assert uploaded.status_code == 201
    assert uploaded.json()["image_url"].startswith("/uploads/comment-images/")
    assert uploaded.json()["image_url"].endswith(".png")

    unsupported = client.post(
        "/api/uploads/comment-images",
        headers=headers,
        files={"file": ("scene.gif", b"GIF89a", "image/gif")},
    )
    assert unsupported.status_code == 400

    too_large = client.post(
        "/api/uploads/comment-images",
        headers=headers,
        files={"file": ("large.jpg", b"\xff\xd8" + (b"x" * (1024 * 1024 + 1)), "image/jpeg")},
    )
    assert too_large.status_code == 413


def test_dish_filters_support_keyword_price_and_area_type(client):
    admin_token = login(client, "root@example.com", "RootPassword123")
    created = create_food_area_dish(client, admin_token, area_type="SNACK_STREET")

    extra = client.post(
        f"/api/admin/vendors/{created['vendor_id']}/dishes",
        headers=auth_headers(admin_token),
        json={"name": "清汤馄饨", "description": "清淡热乎", "price": "8.00", "tag_ids": []},
    )
    assert extra.status_code == 201

    dumplings = client.get("/api/dishes?area_type=SNACK_STREET&keyword=水饺&min_price=10&max_price=20")
    assert dumplings.status_code == 200
    assert [dish["name"] for dish in dumplings.json()] == ["招牌水饺"]

    wonton = client.get("/api/dishes?area_type=SNACK_STREET&keyword=清汤&max_price=10")
    assert wonton.status_code == 200
    assert [dish["name"] for dish in wonton.json()] == ["清汤馄饨"]
