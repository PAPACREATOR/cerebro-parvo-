from mcp.server.fastmcp import FastMCP

mcp = FastMCP("nexus-test-mcp")

@mcp.tool()
def ping(value: str) -> dict:
    return {"echo": value, "authority": "NONE"}

@mcp.tool()
def second(value: int = 1) -> dict:
    return {"value": value * 2}

@mcp.tool()
def explode() -> dict:
    raise ValueError("boom")

if __name__ == "__main__":
    mcp.run(transport="stdio")
