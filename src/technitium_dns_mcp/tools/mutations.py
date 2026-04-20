from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from technitium_dns_mcp.client.base import TechnitiumClient
from technitium_dns_mcp.client.endpoint_catalog import get_endpoint
from technitium_dns_mcp.client.models import RequestParam
from technitium_dns_mcp.guards import (
    require_destructive_confirmation,
    require_mutation_confirmation,
)
from technitium_dns_mcp.validation import (
    normalize_optional_int,
    normalize_optional_name,
    normalize_passthrough_params,
    normalize_passthrough_value,
    validate_dns_name,
    validate_zone_name,
)

DELETE_ALL_STATS_ENDPOINT = get_endpoint("dns_delete_all_stats")
CREATE_PRIMARY_ZONE_ENDPOINT = get_endpoint("dns_create_primary_zone")
CREATE_ZONE_ENDPOINT = get_endpoint("dns_create_zone")
CLONE_ZONE_ENDPOINT = get_endpoint("dns_clone_zone")
CONVERT_ZONE_ENDPOINT = get_endpoint("dns_convert_zone")
ENABLE_ZONE_ENDPOINT = get_endpoint("dns_enable_zone")
DISABLE_ZONE_ENDPOINT = get_endpoint("dns_disable_zone")
DELETE_ZONE_ENDPOINT = get_endpoint("dns_delete_zone")
RESYNC_ZONE_ENDPOINT = get_endpoint("dns_resync_zone")
SET_ZONE_OPTIONS_ENDPOINT = get_endpoint("dns_set_zone_options")
SET_ZONE_PERMISSIONS_ENDPOINT = get_endpoint("dns_set_zone_permissions")
ADD_RECORD_ENDPOINT = get_endpoint("dns_add_record")
UPDATE_RECORD_ENDPOINT = get_endpoint("dns_update_record")
DELETE_RECORD_ENDPOINT = get_endpoint("dns_delete_record")


def _zone_action_params(zone: str) -> dict[str, RequestParam]:
    return {"zone": validate_zone_name(zone)}


def _record_common_params(
    *,
    domain: str,
    zone: str | None = None,
    record_type: str | None = None,
) -> dict[str, RequestParam]:
    return {
        "domain": validate_dns_name(domain),
        "zone": validate_zone_name(zone) if zone is not None else None,
        "type": normalize_optional_name(record_type, field_name="record_type"),
    }


def register_zone_mutation_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_delete_all_stats(confirm: bool = False) -> dict[str, Any]:
        require_destructive_confirmation(confirm=confirm)
        return await client.call_or_throw(DELETE_ALL_STATS_ENDPOINT.api_path)

    @mcp.tool
    async def dns_create_primary_zone(zone: str, confirm: bool = False) -> dict[str, Any]:
        """Create a primary zone after explicit confirmation."""

        require_mutation_confirmation(confirm=confirm)
        return await client.call_or_throw(
            CREATE_PRIMARY_ZONE_ENDPOINT.api_path,
            {"zone": validate_zone_name(zone), "type": "Primary"},
        )

    @mcp.tool
    async def dns_create_zone(
        zone: str,
        zone_type: str,
        options: dict[str, object] | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        params = {
            "zone": validate_zone_name(zone),
            "type": normalize_optional_name(zone_type, field_name="zone_type"),
            **normalize_passthrough_params(options, field_name="options"),
        }
        return await client.call_or_throw(CREATE_ZONE_ENDPOINT.api_path, params)

    @mcp.tool
    async def dns_clone_zone(
        zone: str,
        source_zone: str,
        options: dict[str, object] | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        params = {
            "zone": validate_zone_name(zone),
            "sourceZone": validate_zone_name(source_zone),
            **normalize_passthrough_params(options, field_name="options"),
        }
        return await client.call_or_throw(CLONE_ZONE_ENDPOINT.api_path, params)

    @mcp.tool
    async def dns_convert_zone(
        zone: str,
        zone_type: str,
        options: dict[str, object] | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        params = {
            "zone": validate_zone_name(zone),
            "type": normalize_optional_name(zone_type, field_name="zone_type"),
            **normalize_passthrough_params(options, field_name="options"),
        }
        return await client.call_or_throw(CONVERT_ZONE_ENDPOINT.api_path, params)

    @mcp.tool
    async def dns_enable_zone(zone: str, confirm: bool = False) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        return await client.call_or_throw(ENABLE_ZONE_ENDPOINT.api_path, _zone_action_params(zone))

    @mcp.tool
    async def dns_disable_zone(zone: str, confirm: bool = False) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        return await client.call_or_throw(DISABLE_ZONE_ENDPOINT.api_path, _zone_action_params(zone))

    @mcp.tool
    async def dns_delete_zone(zone: str, confirm: bool = False) -> dict[str, Any]:
        require_destructive_confirmation(confirm=confirm)
        return await client.call_or_throw(DELETE_ZONE_ENDPOINT.api_path, _zone_action_params(zone))

    @mcp.tool
    async def dns_resync_zone(zone: str, confirm: bool = False) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        return await client.call_or_throw(RESYNC_ZONE_ENDPOINT.api_path, _zone_action_params(zone))

    @mcp.tool
    async def dns_set_zone_options(
        zone: str,
        options: dict[str, object] | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        params = {
            "zone": validate_zone_name(zone),
            **normalize_passthrough_params(options, field_name="options"),
        }
        return await client.call_or_throw(SET_ZONE_OPTIONS_ENDPOINT.api_path, params)

    @mcp.tool
    async def dns_set_zone_permissions(
        zone: str,
        user_permissions: object | None = None,
        group_permissions: object | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        params = {
            "zone": validate_zone_name(zone),
            "userPermissions": normalize_passthrough_value(
                user_permissions,
                field_name="user_permissions",
            ),
            "groupPermissions": normalize_passthrough_value(
                group_permissions,
                field_name="group_permissions",
            ),
        }
        return await client.call_or_throw(SET_ZONE_PERMISSIONS_ENDPOINT.api_path, params)

    @mcp.tool
    async def dns_add_record(
        domain: str,
        zone: str | None = None,
        record_type: str | None = None,
        ttl: int | None = None,
        overwrite: bool | None = None,
        comments: str | None = None,
        expiry_ttl: int | None = None,
        record_data: dict[str, object] | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        params = {
            **_record_common_params(domain=domain, zone=zone, record_type=record_type),
            "ttl": normalize_optional_int(ttl, field_name="ttl", minimum=0),
            "overwrite": overwrite,
            "comments": normalize_optional_name(comments, field_name="comments"),
            "expiryTtl": normalize_optional_int(expiry_ttl, field_name="expiry_ttl", minimum=0),
            **normalize_passthrough_params(record_data, field_name="record_data"),
        }
        return await client.call_or_throw(ADD_RECORD_ENDPOINT.api_path, params)

    @mcp.tool
    async def dns_update_record(
        domain: str,
        zone: str | None = None,
        record_type: str | None = None,
        new_domain: str | None = None,
        ttl: int | None = None,
        disable: bool | None = None,
        comments: str | None = None,
        expiry_ttl: int | None = None,
        record_data: dict[str, object] | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        params = {
            **_record_common_params(domain=domain, zone=zone, record_type=record_type),
            "newDomain": validate_dns_name(new_domain) if new_domain is not None else None,
            "ttl": normalize_optional_int(ttl, field_name="ttl", minimum=0),
            "disable": disable,
            "comments": normalize_optional_name(comments, field_name="comments"),
            "expiryTtl": normalize_optional_int(expiry_ttl, field_name="expiry_ttl", minimum=0),
            **normalize_passthrough_params(record_data, field_name="record_data"),
        }
        return await client.call_or_throw(UPDATE_RECORD_ENDPOINT.api_path, params)

    @mcp.tool
    async def dns_delete_record(
        domain: str,
        zone: str | None = None,
        record_type: str | None = None,
        record_selector: dict[str, object] | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_destructive_confirmation(confirm=confirm)
        params = {
            **_record_common_params(domain=domain, zone=zone, record_type=record_type),
            **normalize_passthrough_params(record_selector, field_name="record_selector"),
        }
        return await client.call_or_throw(DELETE_RECORD_ENDPOINT.api_path, params)
