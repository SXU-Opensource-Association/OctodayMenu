from fastapi.testclient import TestClient

from app.main import create_app


def test_health_check():
    client = TestClient(create_app(run_startup=False))

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
