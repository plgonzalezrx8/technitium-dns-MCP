from __future__ import annotations

from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.responses import JSONResponse

from technitium_dns_mcp.client.base import TechnitiumClient
from technitium_dns_mcp.config import Settings, load_settings
from technitium_dns_mcp.tools import (
    register_admin_cluster_mutation_tools,
    register_admin_cluster_tools,
    register_admin_group_mutation_tools,
    register_admin_group_tools,
    register_admin_permission_mutation_tools,
    register_admin_permission_tools,
    register_admin_session_mutation_tools,
    register_admin_session_tools,
    register_admin_user_mutation_tools,
    register_admin_user_tools,
    register_allowed_mutation_tools,
    register_allowed_tools,
    register_app_mutation_tools,
    register_app_tools,
    register_blocked_mutation_tools,
    register_blocked_tools,
    register_cache_mutation_tools,
    register_cache_tools,
    register_dhcp_mutation_tools,
    register_dhcp_tools,
    register_diagnostic_tools,
    register_dns_client_tools,
    register_log_mutation_tools,
    register_log_tools,
    register_settings_mutation_tools,
    register_settings_tools,
    register_zone_dnssec_mutation_tools,
    register_zone_dnssec_tools,
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
        register_zone_dnssec_tools(mcp, resolved_client)
        register_cache_tools(mcp, resolved_client)
        register_allowed_tools(mcp, resolved_client)
        register_blocked_tools(mcp, resolved_client)
        register_app_tools(mcp, resolved_client)
        register_dns_client_tools(mcp, resolved_client)
        register_settings_tools(mcp, resolved_client)
        register_log_tools(mcp, resolved_client)
        register_dhcp_tools(mcp, resolved_client)
        register_admin_session_tools(mcp, resolved_client)
        register_admin_user_tools(mcp, resolved_client)
        register_admin_group_tools(mcp, resolved_client)
        register_admin_permission_tools(mcp, resolved_client)
        register_admin_cluster_tools(mcp, resolved_client)
        if resolved_settings is not None and not resolved_settings.technitium_readonly:
            register_zone_mutation_tools(mcp, resolved_client)
            register_zone_dnssec_mutation_tools(mcp, resolved_client)
            register_cache_mutation_tools(mcp, resolved_client)
            register_allowed_mutation_tools(mcp, resolved_client)
            register_blocked_mutation_tools(mcp, resolved_client)
            register_app_mutation_tools(mcp, resolved_client)
            register_settings_mutation_tools(mcp, resolved_client)
            register_log_mutation_tools(mcp, resolved_client)
            register_dhcp_mutation_tools(mcp, resolved_client)
            register_admin_session_mutation_tools(mcp, resolved_client)
            register_admin_user_mutation_tools(mcp, resolved_client)
            register_admin_group_mutation_tools(mcp, resolved_client)
            register_admin_permission_mutation_tools(mcp, resolved_client)
            register_admin_cluster_mutation_tools(mcp, resolved_client)

    return mcp


def create_http_app() -> Starlette:
    return build_mcp_server().http_app(path="/mcp")
