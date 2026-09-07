from __future__ import annotations

import os
import secrets
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from agent import AgentUnavailableError, responder
from mcp_server import mcp


ROOT = Path(__file__).resolve().parent
mcp_app = mcp.http_app(path="/")
app = FastAPI(
    title="Analizador de riesgo SQL",
    version="0.2.0",
    lifespan=mcp_app.lifespan,
)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    pregunta: str = Field(min_length=1, max_length=25_000)


class ChatResponse(BaseModel):
    respuesta: str


def _configured_key() -> str:
    return os.getenv("APP_ACCESS_KEY", "").strip()


def _presented_key(request: Request) -> str:
    direct = request.headers.get("X-API-Key", "").strip()
    authorization = request.headers.get("Authorization", "")
    if direct:
        return direct
    if authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return ""


@app.middleware("http")
async def protect_api(request: Request, call_next):
    if request.url.path.startswith(("/api/chat", "/api/mcp")):
        expected = _configured_key()
        if not expected:
            return JSONResponse(
                status_code=503,
                content={"error": {"code": "SECURITY_NOT_CONFIGURED", "message": "La clave de acceso no está configurada."}},
            )
        if not secrets.compare_digest(_presented_key(request), expected):
            return JSONResponse(
                status_code=401,
                headers={"WWW-Authenticate": "Bearer"},
                content={"error": {"code": "UNAUTHORIZED", "message": "Clave de acceso inválida."}},
            )
    return await call_next(request)


@app.exception_handler(AgentUnavailableError)
async def unavailable_handler(_: Request, exc: AgentUnavailableError) -> JSONResponse:
    return JSONResponse(status_code=503, content={"error": {"code": "DEPENDENCY_UNAVAILABLE", "message": str(exc)}})


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(ROOT / "index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "authentication": "api-key"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    configured_mcp_url = os.getenv("MCP_URL", "").strip()
    mcp_url = configured_mcp_url or f"{str(request.base_url).rstrip('/')}/api/mcp/"
    return ChatResponse(respuesta=await responder(payload.pregunta, mcp_url=mcp_url))


app.mount("/api/mcp", mcp_app)
