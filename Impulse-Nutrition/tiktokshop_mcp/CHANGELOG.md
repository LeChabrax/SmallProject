# Changelog

## [unreleased] - 2026-04-17

### Changed
- MCP moved from standalone repo (`../Tiktok/MCP-TikTokShop/`) to
  Impulse-Nutrition workspace as `tiktokshop_mcp/`. External npm
  publishing abandoned (project was a test with no external traction).
- Credentials sourcing : `.env` at `tiktokshop_mcp/.env` via `dotenv` is
  now the single source of truth. `.mcp.json` no longer duplicates
  tokens — only `command` + `args`.

### Added
- Auto-refresh of `access_token` using stored `refresh_token`.
  - `client.ts` checks `expires_at` before each request; refreshes
    proactively if expiring within 60s.
  - Fallback : on `105002 Expired credentials`, refreshes and retries
    the request once.
  - Persists new `access_token` + `refresh_token` + `expires_at` back
    to `tiktokshop_mcp/.env` (preserving all other keys).
  - Concurrent-safe : single in-flight refresh promise shared across
    simultaneous requests.
  - Clear error message if `refresh_token` itself has expired, telling
    the user to run `npm run auth` again.
- `setup.ts` now writes `TIKTOK_SHOP_EXPIRES_AT` to `.env` on first
  auth, so the MCP has the expiry known from boot.
- `src/index.ts` loads `.env` via `import "dotenv/config"` at startup.

## [previous unreleased] - 2026-04-16

### Removed
- Product reviews tools (`list_reviews`, `reply_to_review`). The TikTok
  Shop API endpoints for product reviews could not be located via the
  public documentation (gated) and the previously coded path
  `POST product/202309/reviews/search` returned `36009009 Invalid path`.
  Files removed: `src/api/reviews.ts`, `src/tools/reviews.ts`. To
  reintroduce later, the correct endpoint spec must first be confirmed
  via the TikTok Partner Center (logged-in access).

## [0.1.0] - 2026-03-23

### Added
- Initial release
- TikTok Shop API client with HMAC-SHA256 request signing
- Interactive OAuth setup script (`npm run auth`)
- MCP tools for orders: `list_orders`, `get_order_detail`
- MCP tools for customer conversations: `list_conversations`, `read_conversation`, `reply_to_conversation`
- Support for Claude Desktop and Claude Code configuration
