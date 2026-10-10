
import asyncio
import json

from model import chat
from tools import list_files, read_file, write_file
from mcp_client import MCPClientManager
from memory import save_memory

LOCAL_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List all files available in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file from the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string"}
                },
                "required": ["filename"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write or overwrite a file in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["filename", "content"],
            },
        },
    },
   
{
    "type": "function",
    "function": {
        "name": "save_memory",
        "description": (
            "Save useful information for future conversations. "
            "Use when the user explicitly asks you to remember "
            "something or confirms that information should be saved."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "information": {
                    "type": "string",
                    "description": "The information to remember.",
                }
            },
            "required": ["information"],
        },
    },
},

]

LOCAL_FUNCTIONS = {
    "list_files": list_files,
    "read_file": read_file,
    "write_file": write_file,
    "save_memory": save_memory,
}


def to_openai_tool(mcp_tool):
    return {
        "type": "function",
        "function": {
            "name": mcp_tool["name"],
            "description": (
                f"MCP server: {mcp_tool['server']}. "
                f"{mcp_tool['description']}"
            ),
            "parameters": mcp_tool["input_schema"],
        },
    }


async def run_agent_async(messages, mcp):
    discovered = await mcp.list_tools()

    # MCP tool names are mapped to the servers that own them.
    mcp_tool_map = {
        tool["name"]: tool["server"]
        for tool in discovered
    }

    tools = LOCAL_TOOLS + [
        to_openai_tool(tool) for tool in discovered
    ]

    while True:
        response = chat(messages, tools=tools)

        if not response.tool_calls:
            return response.content or ""

        messages.append(response)

        for call in response.tool_calls:
            name = call.function.name

            try:
                args = json.loads(call.function.arguments or "{}")
                print(f"\n[Tool Call] {name} with args: {args}")

                if name in LOCAL_FUNCTIONS:
                    print(f"\n[Local Tool Call] {name} with args: {args}")

                    result = LOCAL_FUNCTIONS[name](**args)

                    if name == "save_memory" and result.get("success"):
                        print(f"\n[Memory Saved] {args.get('information')}")
                        
                elif name in mcp_tool_map:
                    server = mcp_tool_map[name]
                    mcp_result = await mcp.call_tool(
                        server, name, args
                    )

                    result = [
                        item.model_dump()
                        if hasattr(item, "model_dump")
                        else str(item)
                        for item in mcp_result.content
                    ]

                    if mcp_result.is_error:
                        result = {"error": result}

                else:
                    result = {"error": f"Unknown tool: {name}"}

            except Exception as exc:
                result = {"error": str(exc)}

            print(f"\n[Tool Call] {name}")
            print(f"[Tool Result] {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result, ensure_ascii=False),
            })


async def main():
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant. "
                "Use tools when needed. "
                "use MCP time tools for time relevant questions. "
                "For requests to inspect webpages, use the fetch tool. "
                "For workspace files, use the local file tools."
            ),
        }
    ]

    async with MCPClientManager() as mcp:
        while True:
            try:
                question = input("\nyou: ")

                if question.lower() in {"exit", "quit"}:
                    print("bye!")
                    break

                messages.append({
                    "role": "user",
                    "content": question,
                })

                answer = await run_agent_async(messages, mcp)

                messages.append({
                    "role": "assistant",
                    "content": answer,
                })

                print("\nassistant:", answer)

            except (EOFError, KeyboardInterrupt):
                print("\nbye!")
                break


if __name__ == "__main__":
    asyncio.run(main())
