"""FastMCP server entry point for Instagram DM tools.

Keep this file small: just the FastMCP app, the credentials/login
boilerplate, and the register_all() call that wires tools/*.py onto
the server. Individual tool handlers live under `tools/`.
"""

from __future__ import annotations

import argparse
import logging
import os

from dotenv import load_dotenv
from instagrapi import Client
from mcp.server.fastmcp import FastMCP

from .client import login_client
from .tools import register_all

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

INSTRUCTIONS = """
This server is used to send messages to a user on Instagram.
"""

client = Client()

mcp = FastMCP(
    name="Instagram DMs",
    instructions=INSTRUCTIONS,
)

register_all(mcp, client)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", type=str, help="Instagram username (can also be set via INSTAGRAM_USERNAME env var)")
    parser.add_argument("--password", type=str, help="Instagram password (can also be set via INSTAGRAM_PASSWORD env var)")
    args = parser.parse_args()

    username = args.username or os.getenv("INSTAGRAM_USERNAME")
    password = args.password or os.getenv("INSTAGRAM_PASSWORD")

    if not username or not password:
        logger.error("Instagram credentials not provided. Please set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD environment variables in a .env file, or provide --username and --password arguments.")
        print("Error: Instagram credentials not provided.")
        print("Please either:")
        print("1. Create a .env file with INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD")
        print("2. Use --username and --password command line arguments")
        exit(1)

    try:
        logger.info("Attempting to login to Instagram...")
        login_client(client, username, password)
        logger.info("Successfully logged in to Instagram")
        mcp.run(transport="stdio")
    except Exception as e:
        logger.error(f"Failed to login to Instagram: {str(e)}")
        print(f"Error: Failed to login to Instagram - {str(e)}")
        exit(1)
