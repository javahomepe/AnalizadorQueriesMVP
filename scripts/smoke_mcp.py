import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent import discover_tools


async def main() -> None:
    tools = await discover_tools()
    names = [tool.name for tool in tools]
    assert "analizar_riesgo_query" in names
    print("Tools MCP descubiertas:", names)


if __name__ == "__main__":
    asyncio.run(main())
