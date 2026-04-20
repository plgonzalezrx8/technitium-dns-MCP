from __future__ import annotations

from fastmcp import FastMCP

from technitium_dns_mcp.client.base import TechnitiumClient
from technitium_dns_mcp.client.endpoint_catalog import get_endpoint

SETTINGS_ENDPOINT = get_endpoint("dns_get_settings")


def register_diagnostic_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_get_settings() -> dict[str, object]:
        return await client.call_or_throw(SETTINGS_ENDPOINT.api_path)

    @mcp.tool
    async def dns_health_check() -> dict[str, object]:
        settings = await client.call_or_throw(SETTINGS_ENDPOINT.api_path)
        stats = await client.call_or_throw("/api/dashboard/stats/get")
        return {
            "version": settings.get("version"),
            "defaultRecordTtl": settings.get("defaultRecordTtl"),
            "stats": stats.get("stats", {}),
        }
