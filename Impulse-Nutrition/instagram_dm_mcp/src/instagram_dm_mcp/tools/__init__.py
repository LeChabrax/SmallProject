"""MCP tool groups for the Instagram DM server.

Each submodule exposes a `register(mcp, client)` function that registers
its tools on the given FastMCP instance. The server wires them all up in
`server.py` with a handful of register() calls instead of defining 24
tools inline.
"""

from . import send, threads, users, posts, media, misc


def register_all(mcp, client) -> None:
    """Register every tool group on the FastMCP server."""
    send.register(mcp, client)
    threads.register(mcp, client)
    users.register(mcp, client)
    posts.register(mcp, client)
    media.register(mcp, client)
    misc.register(mcp, client)
