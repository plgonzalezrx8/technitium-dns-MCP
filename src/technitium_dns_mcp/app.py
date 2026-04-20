from __future__ import annotations

from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.responses import JSONResponse

from technitium_dns_mcp.client.base import TechnitiumClient
from technitium_dns_mcp.config import Settings, load_settings
from technitium_dns_mcp.tools import (
    register_diagnostic_tools,
    register_zone_mutation_tools,
    register_zone_tools,
)

SERVICE_NAME = "technitium-dns-mcp"


def build_mcp_server(
    settings: Settings | None = None, client: TechnitiumClient | None = None
) -> FastMCP:
    mcp = FastMCP(SERVICE_NAME)

    @mcp.custom_route("/health", methods=["GET"])
    async def health_check(request):  # type: ignore[no-untyped-def]
        return JSONResponse({"status": "ok", "service": SERVICE_NAME})

    resolved_settings = settings
    resolved_client = client
    if resolved_client is None:
        try:
            resolved_settings = settings or load_settings()
        except ValueError:
            resolved_settings = None
        if resolved_settings is not None:
            resolved_client = TechnitiumClient(
                base_url=resolved_settings.technitium_url,
                token=resolved_settings.technitium_token or "",
                verify=resolved_settings.technitium_verify_ssl,
            )

    if resolved_client is not None:
        register_diagnostic_tools(mcp, resolved_client)
        register_zone_tools(mcp, resolved_client)
        if resolved_settings is not None and not resolved_settings.technitium_readonly:
            register_zone_mutation_tools(mcp, resolved_client)

    return mcp


def create_http_app() -> Starlette:
    return build_mcp_server().http_app(path="/mcp")
