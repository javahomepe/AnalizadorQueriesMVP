from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from agent import AgentUnavailableError, responder


ROOT = Path(__file__).resolve().parents[1]
app = FastAPI(title="Analizador de riesgo SQL", version="0.1.0")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    pregunta: str = Field(min_length=1, max_length=25_000)


class ChatResponse(BaseModel):
    respuesta: str


@app.exception_handler(AgentUnavailableError)
async def unavailable_handler(_: Request, exc: AgentUnavailableError) -> JSONResponse:
    return JSONResponse(status_code=503, content={"error": {"code": "DEPENDENCY_UNAVAILABLE", "message": str(exc)}})


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(ROOT / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    return ChatResponse(respuesta=await responder(request.pregunta))

