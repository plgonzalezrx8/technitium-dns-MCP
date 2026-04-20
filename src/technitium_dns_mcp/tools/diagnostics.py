from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from technitium_dns_mcp.client.base import TechnitiumClient
from technitium_dns_mcp.client.endpoint_catalog import get_endpoint
from technitium_dns_mcp.validation import (
    normalize_name,
    normalize_optional_int,
    normalize_optional_name,
)

SETTINGS_ENDPOINT = get_endpoint("dns_get_settings")
TOP_STATS_ENDPOINT = get_endpoint("dns_get_top_stats")


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

    @mcp.tool
    async def dns_get_top_stats(
        type: str,
        stats_type: str,
        limit: int | None = None,
        start: str | None = None,
        end: str | None = None,
        no_reverse_lookup: bool | None = None,
        only_rate_limited_clients: bool | None = None,
        node: str | None = None,
    ) -> dict[str, Any]:
        params = {
            "type": normalize_name(type, field_name="type"),
            "statsType": normalize_name(stats_type, field_name="stats_type"),
            "limit": normalize_optional_int(limit, field_name="limit", minimum=1),
            "start": normalize_optional_name(start, field_name="start"),
            "end": normalize_optional_name(end, field_name="end"),
            "noReverseLookup": no_reverse_lookup,
            "onlyRateLimitedClients": only_rate_limited_clients,
            "node": normalize_optional_name(node, field_name="node"),
        }
        return await client.call_or_throw(TOP_STATS_ENDPOINT.api_path, params)
