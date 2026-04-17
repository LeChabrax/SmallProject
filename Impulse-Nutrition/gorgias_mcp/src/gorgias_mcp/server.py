"""FastMCP entry point — registers every tool from `tools.py`."""

import logging

from mcp.server.fastmcp import FastMCP

from . import tools

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

INSTRUCTIONS = """
This server provides access to Gorgias customer support tickets for Impulse Nutrition.
Use it to search, list and read support tickets and customers, and to send replies.

Filtering: list_tickets accepts status (open/closed/snoozed/unassigned/all),
channel (email/contact_form/chat/help_center), or a raw view_id. Filtering
goes through Gorgias views internally — the legacy ?status= query param is
broken in V2.
"""

mcp = FastMCP(name="Gorgias", instructions=INSTRUCTIONS)


# Register every public function from tools.py as an MCP tool. The list is
# explicit (not introspected) so reordering or renames stay obvious.
_TOOLS = [
    tools.list_tickets,
    tools.list_views,
    tools.get_ticket,
    tools.list_ticket_messages,
    tools.search_tickets,
    tools.get_ticket_stats,
    tools.list_customers,
    tools.get_customer,
    tools.search_customers,
    tools.list_tags,
    tools.reply_to_ticket,
    tools.close_ticket,
    tools.assign_ticket,
]

for fn in _TOOLS:
    mcp.tool()(fn)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
