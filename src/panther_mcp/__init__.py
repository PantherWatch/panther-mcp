from .server import mcp


def main():
    """Run MCP server with stdio transport (local install via uvx)."""
    mcp.run()


def serve():
    """Run MCP server with Streamable HTTP transport (remote/hosted)."""
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8001)
