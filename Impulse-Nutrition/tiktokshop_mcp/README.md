# mcp-tiktokshop

[![npm version](https://img.shields.io/npm/v/mcp-tiktokshop)](https://www.npmjs.com/package/mcp-tiktokshop)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP SDK](https://img.shields.io/badge/MCP_SDK-1.27-blue)](https://modelcontextprotocol.io)
[![Node.js](https://img.shields.io/badge/Node.js-%3E%3D18-green)](https://nodejs.org)

A [Model Context Protocol](https://modelcontextprotocol.io) (MCP) server for **TikTok Shop**. Lets AI assistants like Claude manage orders and respond to customer messages — directly from your conversation.

## Tools

### Orders

| Tool | Description | Parameters |
|------|-------------|------------|
| `list_orders` | Search orders with filters | `page_size`, `page_token`, `order_status`, `sort_field`, `sort_order` |
| `get_order_detail` | Get full details for orders by ID | `order_ids` (array) |

### Customer Conversations

| Tool | Description | Parameters |
|------|-------------|------------|
| `list_conversations` | List customer service conversations | `page_size`, `page_token` |
| `read_conversation` | Read message history | `conversation_id`, `page_size`, `page_token` |
| `reply_to_conversation` | Send a reply to a customer | `conversation_id`, `content` |

> **Note:** Customer Conversations require a specific API scope that may need approval from TikTok. Orders work out of the box.

## Prerequisites

- Node.js >= 18
- A TikTok Shop seller account
- An app on [TikTok Shop Partner Center](https://partner.tiktokshop.com)

## Installation

```bash
npm install -g mcp-tiktokshop
```

Or from source:

```bash
git clone https://github.com/LeChabrax/mcp-tiktokshop.git
cd mcp-tiktokshop
npm install
npm run build
```

## Setup

### 1. Create a TikTok Shop App

1. Go to [TikTok Shop Partner Center](https://partner.tiktokshop.com)
2. Create an app (Custom or Public)
3. Set your redirect URL (any HTTPS URL you control)
4. Enable the API scopes you need:

| Scope | Required for |
|-------|-------------|
| `seller.order.info` | Orders |
| `seller.authorization.info` | Shop info |
| `seller.customer_service` | Conversations (may need approval) |

### 2. Get Your Credentials

Run the interactive setup:

```bash
npm run auth
```

This will:
1. Ask for your App Key and App Secret
2. Open the TikTok authorization page
3. Exchange the code for an access token
4. Fetch your shop cipher
5. Save everything to `.env`

### 3. Configure Your AI Assistant

**Claude Desktop** — edit `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "tiktokshop": {
      "command": "npx",
      "args": ["-y", "mcp-tiktokshop"],
      "env": {
        "TIKTOK_SHOP_APP_KEY": "your_app_key",
        "TIKTOK_SHOP_APP_SECRET": "your_app_secret",
        "TIKTOK_SHOP_ACCESS_TOKEN": "your_access_token",
        "TIKTOK_SHOP_SHOP_CIPHER": "your_shop_cipher"
      }
    }
  }
}
```

**Claude Code** — create `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "tiktokshop": {
      "command": "npx",
      "args": ["-y", "mcp-tiktokshop"],
      "env": {
        "TIKTOK_SHOP_APP_KEY": "your_app_key",
        "TIKTOK_SHOP_APP_SECRET": "your_app_secret",
        "TIKTOK_SHOP_ACCESS_TOKEN": "your_access_token",
        "TIKTOK_SHOP_SHOP_CIPHER": "your_shop_cipher"
      }
    }
  }
}
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TIKTOK_SHOP_APP_KEY` | App Key from Partner Center | Yes |
| `TIKTOK_SHOP_APP_SECRET` | App Secret from Partner Center | Yes |
| `TIKTOK_SHOP_ACCESS_TOKEN` | OAuth2 access token | Yes |
| `TIKTOK_SHOP_SHOP_CIPHER` | Shop identifier | No (some endpoints work without it) |

## How It Works

- **Authentication**: TikTok Shop API uses HMAC-SHA256 request signing. This is handled automatically by the client.
- **Transport**: Uses stdio for local communication with Claude Desktop/Code.
- **Rate Limits**: TikTok Shop allows 50 requests/second per shop.
- **Token Refresh**: Access tokens expire. Re-run `npm run auth` to get a new one.

## Development

```bash
git clone https://github.com/LeChabrax/mcp-tiktokshop.git
cd mcp-tiktokshop
npm install
npm run dev    # Run with hot reload
npm run build  # Compile TypeScript
```

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Areas where help is needed:
- Testing with different TikTok Shop regions (US, UK, SEA)
- Adding support for more API endpoints (products, logistics, fulfillment)
- Token auto-refresh mechanism
- Webhook support for real-time updates

## License

MIT - see [LICENSE](LICENSE)
