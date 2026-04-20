from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from technitium_dns_mcp.client.base import TechnitiumClient
from technitium_dns_mcp.client.endpoint_catalog import get_endpoint
from technitium_dns_mcp.guards import (
    require_destructive_confirmation,
    require_mutation_confirmation,
)
from technitium_dns_mcp.validation import (
    normalize_csv_names,
    normalize_name,
    normalize_optional_name,
)

LIST_BLOCKED_ZONES_ENDPOINT = get_endpoint("dns_list_blocked_zones")
EXPORT_BLOCKED_ZONES_ENDPOINT = get_endpoint("dns_export_blocked_zones")
ADD_BLOCKED_ZONE_ENDPOINT = get_endpoint("dns_add_blocked_zone")
DELETE_BLOCKED_ZONE_ENDPOINT = get_endpoint("dns_delete_blocked_zone")
FLUSH_BLOCKED_ZONES_ENDPOINT = get_endpoint("dns_flush_blocked_zones")
IMPORT_BLOCKED_ZONES_ENDPOINT = get_endpoint("dns_import_blocked_zones")


def register_blocked_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_list_blocked_zones(
        domain: str | None = None,
        direction: str | None = None,
    ) -> dict[str, Any]:
        params = {
            "domain": normalize_optional_name(domain, field_name="domain"),
            "direction": normalize_optional_name(direction, field_name="direction"),
        }
        return await client.call_or_throw(LIST_BLOCKED_ZONES_ENDPOINT.api_path, params)

    @mcp.tool
    async def dns_export_blocked_zones() -> dict[str, Any]:
        response = await client.download(EXPORT_BLOCKED_ZONES_ENDPOINT.api_path)
        return {
            "content": response.content.decode("utf-8"),
            "content_type": response.content_type,
            "filename": response.filename,
        }


def register_blocked_mutation_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_add_blocked_zone(domain: str, confirm: bool = False) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        return await client.call_or_throw(
            ADD_BLOCKED_ZONE_ENDPOINT.api_path,
            {"domain": normalize_name(domain, field_name="domain")},
        )

    @mcp.tool
    async def dns_delete_blocked_zone(domain: str, confirm: bool = False) -> dict[str, Any]:
        require_destructive_confirmation(confirm=confirm)
        return await client.call_or_throw(
            DELETE_BLOCKED_ZONE_ENDPOINT.api_path,
            {"domain": normalize_name(domain, field_name="domain")},
        )

    @mcp.tool
    async def dns_flush_blocked_zones(confirm: bool = False) -> dict[str, Any]:
        require_destructive_confirmation(confirm=confirm)
        return await client.call_or_throw(FLUSH_BLOCKED_ZONES_ENDPOINT.api_path)

    @mcp.tool
    async def dns_import_blocked_zones(
        zones: list[str] | str,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        return await client.call_or_throw(
            IMPORT_BLOCKED_ZONES_ENDPOINT.api_path,
            {"blockedZones": normalize_csv_names(zones, field_name="zones")},
        )
