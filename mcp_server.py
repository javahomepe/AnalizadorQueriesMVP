from __future__ import annotations

from typing import Literal

from fastmcp import FastMCP

from domain.query_analysis import analyze_risk_query


mcp = FastMCP("Analizador de riesgo SQL", stateless_http=True)


@mcp.tool
def analizar_riesgo_query(
    query: str,
    usuario: str,
    perfil_usuario: Literal["analista", "operador", "dba"],
    hora_ejecucion: str,
    intencion: Literal["consulta", "descarga", "proceso_batch"] = "consulta",
    schema_name: str = "query_analyzer",
) -> dict:
    """Analiza cuándo una consulta PostgreSQL de lectura requiere revisión del DBA.

    Úsala cuando el usuario proporcione un SQL y solicite evaluar seguridad, rendimiento,
    horario, volumetría o cumplimiento de políticas. No ejecuta SQL, no modifica datos,
    no recibe credenciales y no concede aprobaciones.
    """
    return analyze_risk_query(query, usuario, perfil_usuario, hora_ejecucion, intencion, schema_name)


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8001, path="/")

