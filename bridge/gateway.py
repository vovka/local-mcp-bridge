"""Build the MCP Streamable HTTP gateway as a Starlette ASGI app.

ponytail: no auth, no allowlist — MVP only. Add bridge/auth + allowlist
filtering (openspec mcp-bridge group 4) before exposing anything you care about.
"""
import contextlib

from mcp import types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Mount

from bridge.config import Config
from bridge.upstream import Upstreams


def _build_server(upstreams: Upstreams) -> Server:
    server: Server = Server("local-mcp-bridge")

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return upstreams.list_tools()

    @server.call_tool(validate_input=False)  # upstream validates; we just proxy
    async def call_tool(name: str, args: dict) -> types.CallToolResult:
        return await upstreams.call(name, args)

    return server


def build_app(cfg: Config) -> Starlette:
    upstreams = Upstreams()
    manager = StreamableHTTPSessionManager(app=_build_server(upstreams), stateless=True)

    @contextlib.asynccontextmanager
    async def lifespan(_app):
        await upstreams.connect(cfg.upstreams)
        async with manager.run():
            yield
        await upstreams.aclose()

    return Starlette(routes=[Mount("/mcp", app=manager.handle_request)], lifespan=lifespan)
