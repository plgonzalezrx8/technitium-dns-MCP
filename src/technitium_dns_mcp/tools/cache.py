from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from technitium_dns_mcp.client.base import TechnitiumClient
from technitium_dns_mcp.client.endpoint_catalog import get_endpoint
from technitium_dns_mcp.guards import require_destructive_confirmation
from technitium_dns_mcp.validation import normalize_name, normalize_optional_name

LIST_CACHE_ENDPOINT = get_endpoint("dns_list_cache")
DELETE_CACHED_ZONE_ENDPOINT = get_endpoint("dns_delete_cached_zone")
FLUSH_CACHE_ENDPOINT = get_endpoint("dns_flush_cache")


def register_cache_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_list_cache(
        domain: str | None = None,
        direction: str | None = None,
    ) -> dict[str, Any]:
        params = {
            "domain": normalize_optional_name(domain, field_name="domain"),
            "direction": normalize_optional_name(direction, field_name="direction"),
        }
        return await client.call_or_throw(LIST_CACHE_ENDPOINT.api_path, params)


def register_cache_mutation_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_delete_cached_zone(domain: str, confirm: bool = False) -> dict[str, Any]:
        require_destructive_confirmation(confirm=confirm)
        return await client.call_or_throw(
            DELETE_CACHED_ZONE_ENDPOINT.api_path,
            {"domain": normalize_name(domain, field_name="domain")},
        )

    @mcp.tool
    async def dns_flush_cache(confirm: bool = False) -> dict[str, Any]:
        require_destructive_confirmation(confirm=confirm)
        return await client.call_or_throw(FLUSH_CACHE_ENDPOINT.api_path)
