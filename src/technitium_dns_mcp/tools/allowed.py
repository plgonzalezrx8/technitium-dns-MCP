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

LIST_ALLOWED_ZONES_ENDPOINT = get_endpoint("dns_list_allowed_zones")
EXPORT_ALLOWED_ZONES_ENDPOINT = get_endpoint("dns_export_allowed_zones")
ADD_ALLOWED_ZONE_ENDPOINT = get_endpoint("dns_add_allowed_zone")
DELETE_ALLOWED_ZONE_ENDPOINT = get_endpoint("dns_delete_allowed_zone")
FLUSH_ALLOWED_ZONES_ENDPOINT = get_endpoint("dns_flush_allowed_zones")
IMPORT_ALLOWED_ZONES_ENDPOINT = get_endpoint("dns_import_allowed_zones")


def register_allowed_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_list_allowed_zones(
        domain: str | None = None,
        direction: str | None = None,
    ) -> dict[str, Any]:
        params = {
            "domain": normalize_optional_name(domain, field_name="domain"),
            "direction": normalize_optional_name(direction, field_name="direction"),
        }
        return await client.call_or_throw(LIST_ALLOWED_ZONES_ENDPOINT.api_path, params)

    @mcp.tool
    async def dns_export_allowed_zones() -> dict[str, Any]:
        response = await client.download(EXPORT_ALLOWED_ZONES_ENDPOINT.api_path)
        return {
            "content": response.content.decode("utf-8"),
            "content_type": response.content_type,
            "filename": response.filename,
        }


def register_allowed_mutation_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_add_allowed_zone(domain: str, confirm: bool = False) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        return await client.call_or_throw(
            ADD_ALLOWED_ZONE_ENDPOINT.api_path,
            {"domain": normalize_name(domain, field_name="domain")},
        )

    @mcp.tool
    async def dns_delete_allowed_zone(domain: str, confirm: bool = False) -> dict[str, Any]:
        require_destructive_confirmation(confirm=confirm)
        return await client.call_or_throw(
            DELETE_ALLOWED_ZONE_ENDPOINT.api_path,
            {"domain": normalize_name(domain, field_name="domain")},
        )

    @mcp.tool
    async def dns_flush_allowed_zones(confirm: bool = False) -> dict[str, Any]:
        require_destructive_confirmation(confirm=confirm)
        return await client.call_or_throw(FLUSH_ALLOWED_ZONES_ENDPOINT.api_path)

    @mcp.tool
    async def dns_import_allowed_zones(
        zones: list[str] | str,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        return await client.call_or_throw(
            IMPORT_ALLOWED_ZONES_ENDPOINT.api_path,
            {"allowedZones": normalize_csv_names(zones, field_name="zones")},
        )
