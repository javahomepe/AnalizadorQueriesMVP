from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    model_id: str
    openrouter_api_key: str
    openrouter_base_url: str
    mcp_url: str
    mcp_timeout_seconds: float
    llm_timeout_seconds: float

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            model_id=os.getenv("MODEL_ID", "openrouter/free"),
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY", "").strip(),
            openrouter_base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/"),
            mcp_url=os.getenv("MCP_URL", "http://127.0.0.1:8001/"),
            mcp_timeout_seconds=float(os.getenv("MCP_TIMEOUT_SECONDS", "30")),
            llm_timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", "90")),
        )


def require_openrouter_key(settings: Settings) -> None:
    if not settings.openrouter_api_key:
        raise RuntimeError("OPENROUTER_API_KEY no está configurada. Copie .env.example a .env y defina la clave.")

