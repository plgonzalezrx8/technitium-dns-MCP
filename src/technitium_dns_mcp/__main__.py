from __future__ import annotations

import uvicorn

from technitium_dns_mcp.app import create_http_app
from technitium_dns_mcp.config import load_settings


def main() -> None:
    settings = load_settings()
    uvicorn.run(create_http_app(), host=settings.mcp_host, port=settings.mcp_port)


if __name__ == "__main__":
    main()
