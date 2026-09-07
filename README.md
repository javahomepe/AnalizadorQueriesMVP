# Analizador de riesgo SQL MVP

MVP local que permite evaluar una consulta PostgreSQL de lectura desde el navegador. Un agente LangChain descubre por HTTP una única tool FastMCP, consulta evidencia sintética y comunica si la solicitud necesita aprobación del DBA. El sistema no ejecuta SQL.

## Arquitectura

```text
index.html + static/app.js
        → POST /api/chat
        → agent.py · LangChain create_agent
        → MultiServerMCPClient
        → api/mcp.py · FastMCP stateless
        → analizar_riesgo_query
        → JSON/XLSX de demostración
```

La decisión de riesgo es determinística. El LLM elige la tool y explica la evidencia, pero no puede cambiar la decisión ni aprobar una ejecución.

## Requisitos

- Python 3.12 o superior.
- Una clave de OpenRouter.
- Dos terminales locales.

## Instalación en Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edite `.env` y defina únicamente:

```text
OPENROUTER_API_KEY=su_clave
```

El modelo predeterminado es `openrouter/free`, que permite a OpenRouter escoger una ruta gratuita compatible con tools. `.env` está excluido de Git.

## Ejecución

Terminal 1, servidor MCP:

```powershell
.\.venv\Scripts\python.exe -m uvicorn api.mcp:app --reload --port 8001
```

Terminal 2, backend y frontend:

```powershell
.\.venv\Scripts\python.exe -m uvicorn api.chat:app --reload --port 8000
```

Abra `http://127.0.0.1:8000`.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Con MCP activo:

```powershell
.\.venv\Scripts\python.exe scripts/smoke_mcp.py
.\.venv\Scripts\python.exe scripts/smoke_agent.py
```

Para comprobar el error de dependencia, detenga el servidor MCP y envíe otra solicitud desde la interfaz. Debe mostrarse un mensaje comprensible, no una respuesta inventada.

## Casos de aceptación

1. Caso feliz: `ops.demo`, perfil `operador`, consulta filtrada a las `09:00`.
2. Caso límite: una tabla inexistente devuelve `evidence_complete=false` y enumera la evidencia faltante.
3. Fuera de alcance: `DELETE`, escrituras o esquemas no autorizados se rechazan.
4. Entrada inválida: SQL vacío u hora inválida devuelven códigos claros.
5. MCP no disponible: `/api/chat` responde `503 DEPENDENCY_UNAVAILABLE`.

## Fuentes de demostración

- `data/schema_demo.json`: esquema autorizado.
- `data/statistics_demo.xlsx`: volumetría aproximada.
- `data/horarios_ejecucion.json`: ventanas de ejecución.
- `data/politicas_tecnicas_queries.json`: límites e incidentes sintéticos.

Los datos son ficticios y no deben sustituirse por datos personales o credenciales. El tamaño de una tabla no es una estimación del resultado de un filtro; sin `EXPLAIN`, el sistema declara esa limitación.

## Alcance y limitaciones

- No ejecuta SQL ni `EXPLAIN`.
- No escribe, borra ni modifica datos.
- No accede a Supabase ni recibe contraseñas de base de datos.
- No implementa una aprobación persistente; solo indica cuándo el DBA debe intervenir.
- FastMCP es stateless; no guarda conversación ni decisiones.
- Vercel es opcional y no está configurado en esta versión.
- La disponibilidad y latencia de modelos gratuitos de OpenRouter pueden variar.

## Continuidad con la PoC

Se reutilizó la capacidad demostrada de AST, selección de metadatos, clasificación horaria y políticas por usuario. Se dejaron fuera del MVP: conexión productiva, `EXPLAIN`, ejecución SQL, múltiples motores, Docker, auditoría WORM y Human-in-the-Loop persistente. Estas piezas pueden incorporarse después de validar el flujo MCP completo.

