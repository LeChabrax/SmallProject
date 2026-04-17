# Contributing to mcp-tiktokshop

Thanks for your interest in contributing! Here's how to get started.

## Development Setup

1. Fork and clone the repo
2. Install dependencies: `npm install`
3. Build: `npm run build`
4. Run in dev mode: `npm run dev`

## Project Structure

```
src/
├── index.ts          # Entry point (stdio transport)
├── server.ts         # MCP server setup & tool registration
├── api/
│   ├── client.ts     # TikTok Shop API client (HMAC signing)
│   ├── orders.ts     # Order endpoints
│   └── conversations.ts  # Customer service endpoints
├── tools/
│   ├── orders.ts     # MCP tool definitions for orders
│   └── conversations.ts  # MCP tool definitions for conversations
└── auth/
    └── setup.ts      # Interactive OAuth setup script
```

## Adding a New Tool

1. Add the API call in `src/api/`
2. Register the MCP tool in `src/tools/`
3. Import and register in `src/server.ts`
4. Update the README tools table
5. Test with `npm run dev`

## Pull Requests

- Keep PRs focused on a single change
- Update documentation if adding new tools
- Make sure `npm run build` passes
- Describe what you changed and why

## TikTok Shop API Notes

- All requests use HMAC-SHA256 signing (handled by `src/api/client.ts`)
- Parameters go in query string, not request body
- API version is `202309` (paths like `/order/202309/orders/search`)
- Rate limit: 50 req/s per shop

## Reporting Issues

- Use GitHub Issues
- Include your Node.js version and error output
- Don't include any credentials or tokens in issues
