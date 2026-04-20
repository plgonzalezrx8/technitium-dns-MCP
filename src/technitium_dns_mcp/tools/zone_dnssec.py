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
    normalize_passthrough_params,
    validate_zone_name,
)

GET_ZONE_DS_INFO_ENDPOINT = get_endpoint("dns_get_zone_ds_info")
GET_ZONE_DNSSEC_PROPERTIES_ENDPOINT = get_endpoint("dns_get_zone_dnssec_properties")
SIGN_ZONE_ENDPOINT = get_endpoint("dns_sign_zone")
UNSIGN_ZONE_ENDPOINT = get_endpoint("dns_unsign_zone")
CONVERT_ZONE_TO_NSEC_ENDPOINT = get_endpoint("dns_convert_zone_to_nsec")
CONVERT_ZONE_TO_NSEC3_ENDPOINT = get_endpoint("dns_convert_zone_to_nsec3")
UPDATE_ZONE_NSEC3_PARAMETERS_ENDPOINT = get_endpoint("dns_update_zone_nsec3_parameters")
UPDATE_ZONE_DNSKEY_TTL_ENDPOINT = get_endpoint("dns_update_zone_dnskey_ttl")
ADD_ZONE_PRIVATE_KEY_ENDPOINT = get_endpoint("dns_add_zone_private_key")
UPDATE_ZONE_PRIVATE_KEY_ENDPOINT = get_endpoint("dns_update_zone_private_key")
DELETE_ZONE_PRIVATE_KEY_ENDPOINT = get_endpoint("dns_delete_zone_private_key")
PUBLISH_ALL_ZONE_PRIVATE_KEYS_ENDPOINT = get_endpoint("dns_publish_all_zone_private_keys")
ROLLOVER_ZONE_DNSKEY_ENDPOINT = get_endpoint("dns_rollover_zone_dnskey")
RETIRE_ZONE_DNSKEY_ENDPOINT = get_endpoint("dns_retire_zone_dnskey")


def _zone_params(zone: str) -> dict[str, str]:
    return {"zone": validate_zone_name(zone)}


def _required_int(value: int | str, *, field_name: str, minimum: int = 0) -> int:
    normalized = normalize_optional_int(value, field_name=field_name, minimum=minimum)
    if normalized is None:
        raise ValueError(f"{field_name} is required")
    return normalized


def register_zone_dnssec_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_get_zone_ds_info(zone: str) -> dict[str, Any]:
        return await client.call_or_throw(GET_ZONE_DS_INFO_ENDPOINT.api_path, _zone_params(zone))

    @mcp.tool
    async def dns_get_zone_dnssec_properties(zone: str) -> dict[str, Any]:
        return await client.call_or_throw(
            GET_ZONE_DNSSEC_PROPERTIES_ENDPOINT.api_path,
            _zone_params(zone),
        )


def register_zone_dnssec_mutation_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_sign_zone(
        zone: str,
        options: dict[str, object] | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        params = {
            "zone": validate_zone_name(zone),
            **normalize_passthrough_params(options, field_name="options"),
        }
        return await client.call_or_throw(SIGN_ZONE_ENDPOINT.api_path, params)

    @mcp.tool
    async def dns_unsign_zone(zone: str, confirm: bool = False) -> dict[str, Any]:
        require_destructive_confirmation(confirm=confirm)
        return await client.call_or_throw(UNSIGN_ZONE_ENDPOINT.api_path, _zone_params(zone))

    @mcp.tool
    async def dns_convert_zone_to_nsec(zone: str, confirm: bool = False) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        return await client.call_or_throw(
            CONVERT_ZONE_TO_NSEC_ENDPOINT.api_path,
            _zone_params(zone),
        )

    @mcp.tool
    async def dns_convert_zone_to_nsec3(
        zone: str,
        iterations: int | str,
        salt_length: int | str,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        params: dict[str, RequestParam] = {
            "zone": validate_zone_name(zone),
            "iterations": _required_int(iterations, field_name="iterations"),
            "saltLength": _required_int(salt_length, field_name="salt_length"),
        }
        return await client.call_or_throw(CONVERT_ZONE_TO_NSEC3_ENDPOINT.api_path, params)

    @mcp.tool
    async def dns_update_zone_nsec3_parameters(
        zone: str,
        iterations: int | str,
        salt_length: int | str,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        params: dict[str, RequestParam] = {
            "zone": validate_zone_name(zone),
            "iterations": _required_int(iterations, field_name="iterations"),
            "saltLength": _required_int(salt_length, field_name="salt_length"),
        }
        return await client.call_or_throw(
            UPDATE_ZONE_NSEC3_PARAMETERS_ENDPOINT.api_path,
            params,
        )

    @mcp.tool
    async def dns_update_zone_dnskey_ttl(
        zone: str,
        dnskey_ttl: int | str,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        params: dict[str, RequestParam] = {
            "zone": validate_zone_name(zone),
            "dnsKeyTtl": _required_int(dnskey_ttl, field_name="dnskey_ttl"),
        }
        return await client.call_or_throw(UPDATE_ZONE_DNSKEY_TTL_ENDPOINT.api_path, params)

    @mcp.tool
    async def dns_add_zone_private_key(
        zone: str,
        key_data: dict[str, object] | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        params: dict[str, RequestParam] = {
            "zone": validate_zone_name(zone),
            **normalize_passthrough_params(key_data, field_name="key_data"),
        }
        return await client.call_or_throw(ADD_ZONE_PRIVATE_KEY_ENDPOINT.api_path, params)

    @mcp.tool
    async def dns_update_zone_private_key(
        zone: str,
        key_tag: int | str,
        rollover_days: int | str,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        params: dict[str, RequestParam] = {
            "zone": validate_zone_name(zone),
            "keyTag": _required_int(key_tag, field_name="key_tag"),
            "rolloverDays": _required_int(rollover_days, field_name="rollover_days"),
        }
        return await client.call_or_throw(UPDATE_ZONE_PRIVATE_KEY_ENDPOINT.api_path, params)

    @mcp.tool
    async def dns_delete_zone_private_key(
        zone: str,
        key_tag: int | str,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_destructive_confirmation(confirm=confirm)
        params: dict[str, RequestParam] = {
            "zone": validate_zone_name(zone),
            "keyTag": _required_int(key_tag, field_name="key_tag"),
        }
        return await client.call_or_throw(DELETE_ZONE_PRIVATE_KEY_ENDPOINT.api_path, params)

    @mcp.tool
    async def dns_publish_all_zone_private_keys(
        zone: str,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        return await client.call_or_throw(
            PUBLISH_ALL_ZONE_PRIVATE_KEYS_ENDPOINT.api_path,
            _zone_params(zone),
        )

    @mcp.tool
    async def dns_rollover_zone_dnskey(
        zone: str,
        key_tag: int | str,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        params: dict[str, RequestParam] = {
            "zone": validate_zone_name(zone),
            "keyTag": _required_int(key_tag, field_name="key_tag"),
        }
        return await client.call_or_throw(ROLLOVER_ZONE_DNSKEY_ENDPOINT.api_path, params)

    @mcp.tool
    async def dns_retire_zone_dnskey(
        zone: str,
        key_tag: int | str,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        params: dict[str, RequestParam] = {
            "zone": validate_zone_name(zone),
            "keyTag": _required_int(key_tag, field_name="key_tag"),
        }
        return await client.call_or_throw(RETIRE_ZONE_DNSKEY_ENDPOINT.api_path, params)
