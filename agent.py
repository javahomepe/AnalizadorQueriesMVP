from __future__ import annotations

from dataclasses import replace
from typing import Any

from langchain.agents import create_agent
from langchain.messages import ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI

from config import Settings, require_openrouter_key
from prompts import SYSTEM_PROMPT


class AgentUnavailableError(RuntimeError):
    pass


async def discover_tools(settings: Settings | None = None) -> list[Any]:
    settings = settings or Settings.from_env()
    client = MultiServerMCPClient({
        "query_risk": {
            "transport": "http",
            "url": settings.mcp_url,
            "headers": {"X-API-Key": settings.access_key} if settings.access_key else {},
        }
    })
    try:
        tools = await client.get_tools()
    except Exception as exc:
        raise AgentUnavailableError("El servidor MCP no está disponible o rechazó la autenticación.") from exc
    if not any(tool.name == "analizar_riesgo_query" for tool in tools):
        raise AgentUnavailableError("MCP respondió, pero no publicó la tool analizar_riesgo_query.")
    return tools


async def responder(
    pregunta: str,
    settings: Settings | None = None,
    *,
    mcp_url: str | None = None,
) -> str:
    pregunta = pregunta.strip() if isinstance(pregunta, str) else ""
    if not pregunta:
        raise ValueError("La pregunta es obligatoria.")
    if len(pregunta) > 25_000:
        raise ValueError("La pregunta supera el límite permitido.")
    settings = settings or Settings.from_env()
    if mcp_url:
        settings = replace(settings, mcp_url=mcp_url)
    require_openrouter_key(settings)
    tools = await discover_tools(settings)
    model = ChatOpenAI(
        model=settings.model_id,
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        temperature=0,
        timeout=settings.llm_timeout_seconds,
        max_retries=1,
        default_headers={"HTTP-Referer": mcp_url or "http://localhost:8000", "X-Title": "AnalizadorQueriesMVP"},
    )
    agent = create_agent(model=model, tools=tools, system_prompt=SYSTEM_PROMPT, name="query_risk_agent")
    try:
        result = await agent.ainvoke({"messages": [{"role": "user", "content": pregunta}]})
    except Exception as exc:
        raise AgentUnavailableError("No fue posible completar el análisis con OpenRouter o la tool MCP.") from exc
    messages = result.get("messages", [])
    if not any(isinstance(message, ToolMessage) and message.name == "analizar_riesgo_query" for message in messages):
        return "No ejecuté el análisis porque faltan datos obligatorios o la solicitud está fuera del alcance. Indique SQL, usuario, perfil, hora, intención y esquema."
    final = messages[-1].content if messages else ""
    if isinstance(final, list):
        final = "\n".join(str(block.get("text", "")) if isinstance(block, dict) else str(block) for block in final)
    return str(final).strip() or "El agente no produjo una respuesta final verificable."
