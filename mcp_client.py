
import asyncio
import json
from contextlib import AsyncExitStack
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from config import MCP_CONFIG_FILE


CONFIG_PATH = Path(__file__).parent / MCP_CONFIG_FILE

class MCPClientManager:

    def __init__(self):
        self.exit_stack = AsyncExitStack()
        self.sessions = {}

    async def __aenter__(self):
        config = json.loads(
            CONFIG_PATH.read_text(encoding="utf-8")
        )

        servers = config.get("mcpServers", {})

        for server_name, server_config in servers.items():
            print(f"[MCP] Connecting to {server_name}...")

            params = StdioServerParameters(
                command=server_config["command"],
                args=server_config.get("args", []),
                env=server_config.get("env"),
            )

            read_stream, write_stream = (
                await self.exit_stack.enter_async_context(
                    stdio_client(params)
                )
            )

            session = await self.exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )

            await session.initialize()

            self.sessions[server_name] = session

            print(f"[MCP] Connected to {server_name}")

        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.exit_stack.aclose()

    async def list_tools(self):
        discovered_tools = []

        for server_name, session in self.sessions.items():
            result = await session.list_tools()

            for tool in result.tools:
                discovered_tools.append({
                    "server": server_name,
                    "name": tool.name,
                    "description": tool.description or "",
                    "input_schema": tool.input_schema,
                })

        return discovered_tools

    def get_server_for_tool(self, tool_name):
        for server_name, session in self.sessions.items():
        # The discovered tools are queried dynamically.
        # Cache them if you want to avoid repeated list_tools calls.
            pass

    async def call_tool(self, server_name, tool_name, arguments):
        session = self.sessions.get(server_name)

        if session is None:
            raise ValueError(
                f"Unknown MCP server: {server_name}"
            )

        return await session.call_tool(
            tool_name,
            arguments=arguments,
        )


async def main():
    async with MCPClientManager() as manager:
        tools = await manager.list_tools()

        print("\n[MCP] Discovered tools:")

        for tool in tools:
            print(f"\nServer: {tool['server']}")
            print(f"Name: {tool['name']}")
            print(f"Description: {tool['description']}")
            print(
                "Input schema: "
                + json.dumps(tool["input_schema"], indent=2)
            )


if __name__ == "__main__":
    asyncio.run(main())
