import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="mcp", args=["run", "server.py"], env=None
)

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List resources and tools
            resources = await session.list_resources()
            tools     = await session.list_tools()
            print("Resources:", [r.name for r in resources.resources])
            print("Tools:    ", [t.name for t in tools.tools])

            # Read greeting
            greeting = await session.read_resource("greeting://hello")
            print("Greeting: ", greeting.contents[0].text)

            # Call add
            result = await session.call_tool("add", {"a": 1, "b": 7})
            print("1 + 7 =  ", result.content[0].text)

if __name__ == "__main__":
    asyncio.run(run())
