"""Connect to upstream stdio MCP servers and route tool calls to them."""
import contextlib

from mcp import types
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from bridge.config import Upstream


class Upstreams:
    """Live stdio sessions to each upstream, with tool-name -> session routing."""

    def __init__(self) -> None:
        self._stack = contextlib.AsyncExitStack()
        self._tools: list[types.Tool] = []
        self._route: dict[str, ClientSession] = {}

    async def connect(self, upstreams: list[Upstream]) -> None:
        for up in upstreams:
            await self._connect_one(up)

    async def _connect_one(self, up: Upstream) -> None:
        session = await self._open_session(up)
        for tool in (await session.list_tools()).tools:
            self._tools.append(tool)
            self._route[tool.name] = session

    async def _open_session(self, up: Upstream) -> ClientSession:
        params = StdioServerParameters(command=up.command, args=up.args)
        read, write = await self._stack.enter_async_context(stdio_client(params))
        session = await self._stack.enter_async_context(ClientSession(read, write))
        await session.initialize()
        return session

    def list_tools(self) -> list[types.Tool]:
        return self._tools

    async def call(self, name: str, args: dict) -> types.CallToolResult:
        session = self._route.get(name)
        if session is None:
            raise ValueError(f"unknown tool: {name}")
        return await session.call_tool(name, args)

    async def aclose(self) -> None:
        await self._stack.aclose()
