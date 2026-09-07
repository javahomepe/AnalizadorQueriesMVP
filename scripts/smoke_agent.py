import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent import responder


QUESTION = """Analiza el riesgo de esta consulta.
Usuario: ops.demo. Perfil: operador. Hora: 09:00. Intención: consulta.
Esquema: query_analyzer.
SQL: SELECT id, customer_id, status FROM query_analyzer.orders WHERE id = 42
"""


if __name__ == "__main__":
    print(asyncio.run(responder(QUESTION)))
