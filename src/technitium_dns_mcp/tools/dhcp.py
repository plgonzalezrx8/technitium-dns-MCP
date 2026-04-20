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
    normalize_ip_address,
    normalize_name,
    normalize_optional_name,
    normalize_passthrough_params,
)

LIST_DHCP_LEASES_ENDPOINT = get_endpoint("dns_list_dhcp_leases")
REMOVE_DHCP_LEASE_ENDPOINT = get_endpoint("dns_remove_dhcp_lease")
CONVERT_DHCP_LEASE_TO_RESERVED_ENDPOINT = get_endpoint("dns_convert_dhcp_lease_to_reserved")
CONVERT_DHCP_LEASE_TO_DYNAMIC_ENDPOINT = get_endpoint("dns_convert_dhcp_lease_to_dynamic")
LIST_DHCP_SCOPES_ENDPOINT = get_endpoint("dns_list_dhcp_scopes")
GET_DHCP_SCOPE_ENDPOINT = get_endpoint("dns_get_dhcp_scope")
SET_DHCP_SCOPE_ENDPOINT = get_endpoint("dns_set_dhcp_scope")
ADD_DHCP_RESERVED_LEASE_ENDPOINT = get_endpoint("dns_add_dhcp_reserved_lease")
REMOVE_DHCP_RESERVED_LEASE_ENDPOINT = get_endpoint("dns_remove_dhcp_reserved_lease")
ENABLE_DHCP_SCOPE_ENDPOINT = get_endpoint("dns_enable_dhcp_scope")
DISABLE_DHCP_SCOPE_ENDPOINT = get_endpoint("dns_disable_dhcp_scope")
DELETE_DHCP_SCOPE_ENDPOINT = get_endpoint("dns_delete_dhcp_scope")


def _scope_name(name: str) -> str:
    return normalize_name(name, field_name="name")


def _lease_selector_params(
    *,
    name: str,
    hardware_address: str | None,
    client_identifier: str | None,
) -> dict[str, RequestParam]:
    normalized_hardware_address = normalize_optional_name(
        hardware_address,
        field_name="hardware_address",
    )
    normalized_client_identifier = normalize_optional_name(
        client_identifier,
        field_name="client_identifier",
    )
    if normalized_hardware_address is None and normalized_client_identifier is None:
        raise ValueError("Provide hardware_address or client_identifier.")
    return {
        "name": _scope_name(name),
        "hardwareAddress": normalized_hardware_address,
        "clientIdentifier": normalized_client_identifier,
    }


def register_dhcp_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_list_dhcp_leases() -> dict[str, Any]:
        return await client.call_or_throw(LIST_DHCP_LEASES_ENDPOINT.api_path)

    @mcp.tool
    async def dns_list_dhcp_scopes() -> dict[str, Any]:
        return await client.call_or_throw(LIST_DHCP_SCOPES_ENDPOINT.api_path)

    @mcp.tool
    async def dns_get_dhcp_scope(name: str) -> dict[str, Any]:
        return await client.call_or_throw(
            GET_DHCP_SCOPE_ENDPOINT.api_path,
            {"name": _scope_name(name)},
        )


def register_dhcp_mutation_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_remove_dhcp_lease(
        name: str,
        hardware_address: str | None = None,
        client_identifier: str | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_destructive_confirmation(confirm=confirm)
        return await client.call_or_throw(
            REMOVE_DHCP_LEASE_ENDPOINT.api_path,
            _lease_selector_params(
                name=name,
                hardware_address=hardware_address,
                client_identifier=client_identifier,
            ),
        )

    @mcp.tool
    async def dns_convert_dhcp_lease_to_reserved(
        name: str,
        hardware_address: str | None = None,
        client_identifier: str | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        return await client.call_or_throw(
            CONVERT_DHCP_LEASE_TO_RESERVED_ENDPOINT.api_path,
            _lease_selector_params(
                name=name,
                hardware_address=hardware_address,
                client_identifier=client_identifier,
            ),
        )

    @mcp.tool
    async def dns_convert_dhcp_lease_to_dynamic(
        name: str,
        hardware_address: str | None = None,
        client_identifier: str | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        return await client.call_or_throw(
            CONVERT_DHCP_LEASE_TO_DYNAMIC_ENDPOINT.api_path,
            _lease_selector_params(
                name=name,
                hardware_address=hardware_address,
                client_identifier=client_identifier,
            ),
        )

    @mcp.tool
    async def dns_set_dhcp_scope(
        name: str,
        options: dict[str, object] | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        params = {
            "name": _scope_name(name),
            **normalize_passthrough_params(options, field_name="options"),
        }
        return await client.call_or_throw(SET_DHCP_SCOPE_ENDPOINT.api_path, params)

    @mcp.tool
    async def dns_add_dhcp_reserved_lease(
        name: str,
        hardware_address: str,
        ip_address: str,
        host_name: str | None = None,
        comments: str | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        params = {
            "name": _scope_name(name),
            "hardwareAddress": normalize_name(hardware_address, field_name="hardware_address"),
            "ipAddress": normalize_ip_address(ip_address, field_name="ip_address"),
            "hostName": normalize_optional_name(host_name, field_name="host_name"),
            "comments": normalize_optional_name(comments, field_name="comments"),
        }
        return await client.call_or_throw(ADD_DHCP_RESERVED_LEASE_ENDPOINT.api_path, params)

    @mcp.tool
    async def dns_remove_dhcp_reserved_lease(
        name: str,
        hardware_address: str,
        confirm: bool = False,
    ) -> dict[str, Any]:
        require_destructive_confirmation(confirm=confirm)
        return await client.call_or_throw(
            REMOVE_DHCP_RESERVED_LEASE_ENDPOINT.api_path,
            {
                "name": _scope_name(name),
                "hardwareAddress": normalize_name(
                    hardware_address,
                    field_name="hardware_address",
                ),
            },
        )

    @mcp.tool
    async def dns_enable_dhcp_scope(name: str, confirm: bool = False) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        return await client.call_or_throw(
            ENABLE_DHCP_SCOPE_ENDPOINT.api_path,
            {"name": _scope_name(name)},
        )

    @mcp.tool
    async def dns_disable_dhcp_scope(name: str, confirm: bool = False) -> dict[str, Any]:
        require_mutation_confirmation(confirm=confirm)
        return await client.call_or_throw(
            DISABLE_DHCP_SCOPE_ENDPOINT.api_path,
            {"name": _scope_name(name)},
        )

    @mcp.tool
    async def dns_delete_dhcp_scope(name: str, confirm: bool = False) -> dict[str, Any]:
        require_destructive_confirmation(confirm=confirm)
        return await client.call_or_throw(
            DELETE_DHCP_SCOPE_ENDPOINT.api_path,
            {"name": _scope_name(name)},
        )
