# Contexto del proyecto

## Producto

MVP para que analistas y operadores evalúen el riesgo de una consulta SQL de lectura antes de solicitar su ejecución en producción.

## Alcance

Sí hace: analiza una única consulta PostgreSQL de solo lectura, consulta metadatos y políticas sintéticas, y determina si requiere revisión del DBA.

No hace: no ejecuta SQL, no modifica bases, no recibe credenciales de base de datos, no aprueba en nombre del DBA y no inventa evidencia ausente.

## Arquitectura

- Frontend: HTML y JavaScript estático.
- Backend: FastAPI en `api/chat.py`, con `POST /api/chat`.
- Agente: LangChain `create_agent` en `agent.py`.
- Tools: FastMCP stateless en `mcp_server.py` y `api/mcp.py`.
- Descubrimiento: `MultiServerMCPClient` por HTTP; no importar la tool desde `agent.py`.
- Datos: JSON y XLSX sintéticos bajo `data/`.

## Reglas

- Mantener una sola capacidad MCP: `analizar_riesgo_query`.
- Priorizar funciones de solo lectura y validación deny-by-default.
- No guardar secretos, queries originales ni datos personales en logs o Git.
- No presentar estimaciones como mediciones reales.
- Agregar o ajustar pruebas cuando cambie el comportamiento.
- Ejecutar pruebas antes de declarar una funcionalidad terminada.

## Criterios de aceptación

1. Un caso feliz usa la tool y devuelve evidencia.
2. Un caso límite declara evidencia faltante sin inventar.
3. Una operación fuera de alcance se rechaza.
4. Una entrada inválida devuelve un error comprensible.
5. El backend informa claramente cuando MCP o OpenRouter no están disponibles.

