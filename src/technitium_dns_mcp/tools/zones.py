from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from technitium_dns_mcp.client.base import TechnitiumClient
from technitium_dns_mcp.client.endpoint_catalog import get_endpoint
from technitium_dns_mcp.validation import validate_dns_name, validate_zone_name

LIST_ZONES_ENDPOINT = get_endpoint("dns_list_zones")
LIST_CATALOG_ZONES_ENDPOINT = get_endpoint("dns_list_catalog_zones")
GET_ZONE_OPTIONS_ENDPOINT = get_endpoint("dns_get_zone_options")
GET_ZONE_PERMISSIONS_ENDPOINT = get_endpoint("dns_get_zone_permissions")
GET_RECORDS_ENDPOINT = get_endpoint("dns_get_records")


def register_zone_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_list_zones() -> dict[str, object]:
        return await client.call_or_throw(LIST_ZONES_ENDPOINT.api_path)

    @mcp.tool
    async def dns_list_catalog_zones() -> dict[str, object]:
        return await client.call_or_throw(LIST_CATALOG_ZONES_ENDPOINT.api_path)

    @mcp.tool
    async def dns_get_zone_options(
        zone: str,
        include_available_catalog_zone_names: bool | None = None,
        include_available_tsig_key_names: bool | None = None,
    ) -> dict[str, Any]:
        params = {
            "zone": validate_zone_name(zone),
            "includeAvailableCatalogZoneNames": include_available_catalog_zone_names,
            "includeAvailableTsigKeyNames": include_available_tsig_key_names,
        }
        return await client.call_or_throw(GET_ZONE_OPTIONS_ENDPOINT.api_path, params)

    @mcp.tool
    async def dns_get_zone_permissions(
        zone: str,
        include_users_and_groups: bool | None = None,
    ) -> dict[str, Any]:
        params = {
            "zone": validate_zone_name(zone),
            "includeUsersAndGroups": include_users_and_groups,
        }
        return await client.call_or_throw(GET_ZONE_PERMISSIONS_ENDPOINT.api_path, params)

    @mcp.tool
    async def dns_get_records(
        domain: str,
        zone: str | None = None,
        list_zone: bool | None = None,
    ) -> dict[str, Any]:
        params = {
            "domain": validate_dns_name(domain),
            "zone": validate_zone_name(zone) if zone is not None else None,
            "listZone": list_zone,
        }
        return await client.call_or_throw(GET_RECORDS_ENDPOINT.api_path, params)
