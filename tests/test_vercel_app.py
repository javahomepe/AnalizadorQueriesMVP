from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_health_is_public() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["authentication"] == "api-key"


def test_chat_fails_closed_without_configured_key(monkeypatch) -> None:
    monkeypatch.delenv("APP_ACCESS_KEY", raising=False)
    response = client.post("/api/chat", json={"pregunta": "consulta"})
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "SECURITY_NOT_CONFIGURED"


def test_chat_rejects_wrong_key(monkeypatch) -> None:
    monkeypatch.setenv("APP_ACCESS_KEY", "clave-correcta")
    response = client.post(
        "/api/chat",
        headers={"X-API-Key": "clave-incorrecta"},
        json={"pregunta": "consulta"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"
