from fastapi.testclient import TestClient

from api import chat as chat_module


client = TestClient(chat_module.app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_contract(monkeypatch):
    async def fake_responder(_: str) -> str:
        return "Evidencia verificada mediante analizar_riesgo_query."

    monkeypatch.setattr(chat_module, "responder", fake_responder)
    response = client.post("/api/chat", json={"pregunta": "Analiza SELECT 1"})
    assert response.status_code == 200
    assert "Evidencia" in response.json()["respuesta"]


def test_chat_rejects_empty_input():
    response = client.post("/api/chat", json={"pregunta": ""})
    assert response.status_code == 422


def test_mcp_unavailable_is_clear(monkeypatch):
    async def unavailable(_: str) -> str:
        raise chat_module.AgentUnavailableError("El servidor MCP no está disponible.")

    monkeypatch.setattr(chat_module, "responder", unavailable)
    response = client.post("/api/chat", json={"pregunta": "Analiza una consulta"})
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "DEPENDENCY_UNAVAILABLE"

