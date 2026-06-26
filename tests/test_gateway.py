"""End-to-end smoke test: drive the bridge over Streamable HTTP like a cloud client.

Run inside the container:  python tests/test_gateway.py
Spawns the gateway, connects an MCP client to http://127.0.0.1:8000/mcp,
lists tools, and reads a known in-root file via the fs upstream.
"""
import anyio
import uvicorn

from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from bridge.config import Config
from bridge.gateway import build_app

URL = "http://127.0.0.1:8000/mcp"


async def _exercise() -> None:
    async with streamablehttp_client(URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            names = [t.name for t in (await session.list_tools()).tools]
            assert "read_file" in names, names
            res = await session.call_tool("read_file", {"path": "/app/pyproject.toml"})
            assert "local-mcp-bridge" in res.content[0].text, res.content[0].text
    print(f"OK: {len(names)} tools, read_file works -> {names}")


async def _exercise_with_retry() -> None:
    for _ in range(50):  # wait for uvicorn to bind
        try:
            return await _exercise()
        except Exception:
            await anyio.sleep(0.2)
    raise SystemExit("gateway never came up")


async def _main() -> None:
    server = uvicorn.Server(uvicorn.Config(build_app(Config.load()), port=8000, log_level="warning"))
    async with anyio.create_task_group() as tg:
        tg.start_soon(server.serve)
        await _exercise_with_retry()
        server.should_exit = True


if __name__ == "__main__":
    anyio.run(_main)
