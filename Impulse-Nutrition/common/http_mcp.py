"""Small HTTP client base used by Gorgias / Shopify / BigBlue MCP servers.

Prior to this refactor, each of the three REST-based MCPs implemented its own
`_get` / `_post` / `_put` / `_delete` helpers with subtle differences in error
handling. `MCPHttpClient` consolidates them:

- Consistent retry behaviour on transient 5xx responses.
- Uniform `error_payload()` that is safe to return from a tool handler.
- Pluggable `base_url` and `default_headers` so each MCP only writes the
  mutable bits (auth, params, body shape).

Usage:

    class GorgiasClient(MCPHttpClient):
        def default_headers(self):
            return {"Accept": "application/json"}

    client = GorgiasClient(base_url="https://impulse.gorgias.com/api",
                           auth=("user@host", "api_key"))
    resp = client.get("/tickets", params={"limit": 10})
"""

from __future__ import annotations

import logging
import time
from typing import Any, Callable, Dict, Optional, Tuple

import requests

logger = logging.getLogger(__name__)


class MCPHttpClient:
    """Small retrying HTTP client suitable for a synchronous MCP tool.

    Subclasses may override `default_headers`, `default_params` and
    `on_response` to inject auth, transform query params, or log specific
    fields. Subclassing is optional — `MCPHttpClient` can be instantiated
    directly with kwargs.
    """

    def __init__(
        self,
        base_url: str,
        *,
        auth: Optional[Tuple[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
        retries: int = 2,
        retry_backoff: float = 1.5,
    ):
        self.base_url = base_url.rstrip("/")
        self.auth = auth
        self._headers = headers or {}
        self.timeout = timeout
        self.retries = retries
        self.retry_backoff = retry_backoff

    def default_headers(self) -> Dict[str, str]:
        return dict(self._headers)

    def _url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return f"{self.base_url}/{path.lstrip('/')}"

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        merged_headers = self.default_headers()
        if headers:
            merged_headers.update(headers)

        last_err: Optional[Exception] = None
        for attempt in range(self.retries + 1):
            try:
                resp = requests.request(
                    method,
                    self._url(path),
                    params=params,
                    json=json,
                    headers=merged_headers,
                    auth=self.auth,
                    timeout=self.timeout,
                )
                if resp.status_code >= 500 and attempt < self.retries:
                    wait = self.retry_backoff ** attempt
                    logger.warning(
                        "HTTP %s %s -> %d, retrying in %.1fs",
                        method, path, resp.status_code, wait,
                    )
                    time.sleep(wait)
                    continue
                resp.raise_for_status()
                if not resp.content:
                    return None
                try:
                    return resp.json()
                except ValueError:
                    return resp.text
            except requests.RequestException as e:
                last_err = e
                if attempt < self.retries:
                    wait = self.retry_backoff ** attempt
                    logger.warning(
                        "HTTP %s %s transient error %s, retrying in %.1fs",
                        method, path, e, wait,
                    )
                    time.sleep(wait)
                    continue
                raise
        if last_err is not None:
            raise last_err

    def get(self, path: str, **kw):
        return self._request("GET", path, **kw)

    def post(self, path: str, **kw):
        return self._request("POST", path, **kw)

    def put(self, path: str, **kw):
        return self._request("PUT", path, **kw)

    def delete(self, path: str, **kw):
        return self._request("DELETE", path, **kw)


def error_payload(
    tool: str,
    exc: Exception,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Return a structured error dict safe to surface from an MCP tool.

    Sensitive keys (`password`, `token`, `authorization`, `api_key`) are
    masked. Always pair with a `logger.exception` call so the full trace is
    captured on the server side.
    """
    masked_params: Dict[str, Any] = {}
    sensitive = {"password", "token", "authorization", "api_key"}
    for k, v in (params or {}).items():
        if any(s in k.lower() for s in sensitive):
            masked_params[k] = "***"
        else:
            masked_params[k] = v
    return {
        "error": str(exc),
        "error_type": type(exc).__name__,
        "tool": tool,
        "params": masked_params,
    }


def safe_call(
    tool: str,
    fn: Callable[..., Any],
    *args,
    **kwargs,
) -> Any:
    """Call `fn` and return its result; on exception return `error_payload`.

    Avoids the pattern of writing `try: ... except Exception as e: return
    {"error": str(e)}` in every MCP tool.
    """
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        logger.exception("tool %s failed", tool)
        return error_payload(tool, e, kwargs)
