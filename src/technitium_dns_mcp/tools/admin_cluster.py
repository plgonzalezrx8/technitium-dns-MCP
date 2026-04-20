from __future__ import annotations

import base64
from collections.abc import Callable, Sequence
from typing import Any

from fastmcp import FastMCP

from technitium_dns_mcp.client.base import TechnitiumClient
from technitium_dns_mcp.client.endpoint_catalog import get_endpoint
from technitium_dns_mcp.client.models import RequestHeaders, RequestParam
from technitium_dns_mcp.guards import (
    require_critical_admin_confirmation,
    require_destructive_confirmation,
)
from technitium_dns_mcp.validation import (
    normalize_ip_address,
    normalize_name,
    normalize_optional_int,
    normalize_passthrough_params,
    validate_zone_name,
)

GET_CLUSTER_STATE_ENDPOINT = get_endpoint("dns_get_cluster_state")
INITIALIZE_CLUSTER_ENDPOINT = get_endpoint("dns_initialize_cluster")
DELETE_CLUSTER_ENDPOINT = get_endpoint("dns_delete_cluster")
JOIN_CLUSTER_ENDPOINT = get_endpoint("dns_join_cluster")
REMOVE_CLUSTER_SECONDARY_NODE_ENDPOINT = get_endpoint("dns_remove_cluster_secondary_node")
DELETE_CLUSTER_SECONDARY_NODE_ENDPOINT = get_endpoint("dns_delete_cluster_secondary_node")
UPDATE_CLUSTER_SECONDARY_NODE_ENDPOINT = get_endpoint("dns_update_cluster_secondary_node")
TRANSFER_CLUSTER_CONFIG_ENDPOINT = get_endpoint("dns_transfer_cluster_config")
SET_CLUSTER_OPTIONS_ENDPOINT = get_endpoint("dns_set_cluster_options")
INITIALIZE_AND_JOIN_CLUSTER_ENDPOINT = get_endpoint("dns_initialize_and_join_cluster")
LEAVE_CLUSTER_ENDPOINT = get_endpoint("dns_leave_cluster")
NOTIFY_CLUSTER_ENDPOINT = get_endpoint("dns_notify_cluster")
RESYNC_CLUSTER_ENDPOINT = get_endpoint("dns_resync_cluster")
UPDATE_CLUSTER_PRIMARY_NODE_ENDPOINT = get_endpoint("dns_update_cluster_primary_node")
PROMOTE_TO_CLUSTER_PRIMARY_ENDPOINT = get_endpoint("dns_promote_to_cluster_primary")
UPDATE_CLUSTER_NODE_IP_ADDRESSES_ENDPOINT = get_endpoint("dns_update_cluster_node_ip_addresses")
CLUSTER_ACKNOWLEDGEMENT = "cluster-admin"


def _required_int(value: int | str, *, field_name: str) -> int:
    normalized = normalize_optional_int(value, field_name=field_name, minimum=0)
    if normalized is None:
        raise ValueError(f"{field_name} is required")
    return normalized


def _csv_values(
    value: Sequence[str] | str,
    *,
    field_name: str,
    normalizer: Callable[[str], str],
) -> str:
    if isinstance(value, str):
        return normalizer(value)
    normalized_values = [normalizer(item) for item in value]
    if not normalized_values:
        raise ValueError(f"{field_name} is required")
    return ",".join(normalized_values)


def _csv_ip_addresses(value: Sequence[str] | str, *, field_name: str) -> str:
    return _csv_values(
        value,
        field_name=field_name,
        normalizer=lambda item: normalize_ip_address(item, field_name=field_name),
    )


def _csv_zones(value: Sequence[str] | str, *, field_name: str) -> str:
    return _csv_values(
        value,
        field_name=field_name,
        normalizer=lambda item: validate_zone_name(item),
    )


def _critical_cluster_confirmation(*, confirm: bool, acknowledge: str | None) -> None:
    require_critical_admin_confirmation(
        confirm=confirm,
        acknowledge=acknowledge,
        expected_acknowledgement=CLUSTER_ACKNOWLEDGEMENT,
    )


def register_admin_cluster_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_get_cluster_state(
        include_server_ip_addresses: bool | None = None,
    ) -> dict[str, Any]:
        return await client.call_or_throw(
            GET_CLUSTER_STATE_ENDPOINT.api_path,
            {"includeServerIpAddresses": include_server_ip_addresses},
        )


def register_admin_cluster_mutation_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_initialize_cluster(
        cluster_domain: str,
        primary_node_ip_addresses: list[str] | str,
        confirm: bool = False,
        acknowledge: str | None = None,
    ) -> dict[str, Any]:
        _critical_cluster_confirmation(confirm=confirm, acknowledge=acknowledge)
        return await client.call_or_throw(
            INITIALIZE_CLUSTER_ENDPOINT.api_path,
            {
                "clusterDomain": validate_zone_name(cluster_domain),
                "primaryNodeIpAddresses": _csv_ip_addresses(
                    primary_node_ip_addresses,
                    field_name="primary_node_ip_addresses",
                ),
            },
        )

    @mcp.tool
    async def dns_delete_cluster(
        force_delete: bool | None = None,
        confirm: bool = False,
        acknowledge: str | None = None,
    ) -> dict[str, Any]:
        require_destructive_confirmation(confirm=confirm)
        _critical_cluster_confirmation(confirm=confirm, acknowledge=acknowledge)
        return await client.call_or_throw(
            DELETE_CLUSTER_ENDPOINT.api_path,
            {"forceDelete": force_delete},
        )

    @mcp.tool
    async def dns_join_cluster(
        secondary_node_id: int | str,
        secondary_node_url: str,
        secondary_node_ip_addresses: list[str] | str,
        secondary_node_certificate: str,
        confirm: bool = False,
        acknowledge: str | None = None,
    ) -> dict[str, Any]:
        _critical_cluster_confirmation(confirm=confirm, acknowledge=acknowledge)
        return await client.call_or_throw(
            JOIN_CLUSTER_ENDPOINT.api_path,
            {
                "secondaryNodeId": _required_int(
                    secondary_node_id,
                    field_name="secondary_node_id",
                ),
                "secondaryNodeUrl": normalize_name(
                    secondary_node_url,
                    field_name="secondary_node_url",
                ),
                "secondaryNodeIpAddresses": _csv_ip_addresses(
                    secondary_node_ip_addresses,
                    field_name="secondary_node_ip_addresses",
                ),
                "secondaryNodeCertificate": normalize_name(
                    secondary_node_certificate,
                    field_name="secondary_node_certificate",
                ),
            },
        )

    @mcp.tool
    async def dns_remove_cluster_secondary_node(
        secondary_node_id: int | str,
        confirm: bool = False,
        acknowledge: str | None = None,
    ) -> dict[str, Any]:
        require_destructive_confirmation(confirm=confirm)
        _critical_cluster_confirmation(confirm=confirm, acknowledge=acknowledge)
        return await client.call_or_throw(
            REMOVE_CLUSTER_SECONDARY_NODE_ENDPOINT.api_path,
            {"secondaryNodeId": _required_int(secondary_node_id, field_name="secondary_node_id")},
        )

    @mcp.tool
    async def dns_delete_cluster_secondary_node(
        secondary_node_id: int | str,
        confirm: bool = False,
        acknowledge: str | None = None,
    ) -> dict[str, Any]:
        require_destructive_confirmation(confirm=confirm)
        _critical_cluster_confirmation(confirm=confirm, acknowledge=acknowledge)
        return await client.call_or_throw(
            DELETE_CLUSTER_SECONDARY_NODE_ENDPOINT.api_path,
            {"secondaryNodeId": _required_int(secondary_node_id, field_name="secondary_node_id")},
        )

    @mcp.tool
    async def dns_update_cluster_secondary_node(
        secondary_node_id: int | str,
        secondary_node_url: str,
        secondary_node_ip_addresses: list[str] | str,
        secondary_node_certificate: str,
        confirm: bool = False,
        acknowledge: str | None = None,
    ) -> dict[str, Any]:
        _critical_cluster_confirmation(confirm=confirm, acknowledge=acknowledge)
        return await client.call_or_throw(
            UPDATE_CLUSTER_SECONDARY_NODE_ENDPOINT.api_path,
            {
                "secondaryNodeId": _required_int(
                    secondary_node_id,
                    field_name="secondary_node_id",
                ),
                "secondaryNodeUrl": normalize_name(
                    secondary_node_url,
                    field_name="secondary_node_url",
                ),
                "secondaryNodeIpAddresses": _csv_ip_addresses(
                    secondary_node_ip_addresses,
                    field_name="secondary_node_ip_addresses",
                ),
                "secondaryNodeCertificate": normalize_name(
                    secondary_node_certificate,
                    field_name="secondary_node_certificate",
                ),
            },
        )

    @mcp.tool
    async def dns_transfer_cluster_config(
        include_zones: list[str] | str | None = None,
        if_modified_since_rfc2822: str | None = None,
        confirm: bool = False,
        acknowledge: str | None = None,
    ) -> dict[str, Any]:
        _critical_cluster_confirmation(confirm=confirm, acknowledge=acknowledge)
        params: dict[str, RequestParam] = {
            "includeZones": (
                _csv_zones(include_zones, field_name="include_zones")
                if include_zones is not None
                else None
            )
        }
        headers: RequestHeaders | None = None
        if if_modified_since_rfc2822 is not None:
            headers = {
                "If-Modified-Since": normalize_name(
                    if_modified_since_rfc2822,
                    field_name="if_modified_since_rfc2822",
                )
            }
        response = await client.download(
            TRANSFER_CLUSTER_CONFIG_ENDPOINT.api_path,
            params,
            headers=headers,
        )
        return {
            "content_base64": base64.b64encode(response.content).decode(),
            "content_type": response.content_type,
            "filename": response.filename,
            "size_bytes": len(response.content),
        }

    @mcp.tool
    async def dns_set_cluster_options(
        options: dict[str, object] | None = None,
        confirm: bool = False,
        acknowledge: str | None = None,
    ) -> dict[str, Any]:
        _critical_cluster_confirmation(confirm=confirm, acknowledge=acknowledge)
        return await client.call_or_throw(
            SET_CLUSTER_OPTIONS_ENDPOINT.api_path,
            normalize_passthrough_params(options, field_name="options"),
        )

    @mcp.tool
    async def dns_initialize_and_join_cluster(
        secondary_node_ip_addresses: list[str] | str,
        primary_node_url: str,
        primary_node_username: str,
        primary_node_password: str,
        primary_node_totp: str | None = None,
        primary_node_ip_address: str | None = None,
        ignore_certificate_errors: bool | None = None,
        confirm: bool = False,
        acknowledge: str | None = None,
    ) -> dict[str, Any]:
        _critical_cluster_confirmation(confirm=confirm, acknowledge=acknowledge)
        return await client.call_or_throw(
            INITIALIZE_AND_JOIN_CLUSTER_ENDPOINT.api_path,
            {
                "secondaryNodeIpAddresses": _csv_ip_addresses(
                    secondary_node_ip_addresses,
                    field_name="secondary_node_ip_addresses",
                ),
                "primaryNodeUrl": normalize_name(
                    primary_node_url,
                    field_name="primary_node_url",
                ),
                "primaryNodeUsername": normalize_name(
                    primary_node_username,
                    field_name="primary_node_username",
                ),
                "primaryNodePassword": normalize_name(
                    primary_node_password,
                    field_name="primary_node_password",
                ),
                "primaryNodeTotp": (
                    normalize_name(primary_node_totp, field_name="primary_node_totp")
                    if primary_node_totp is not None
                    else None
                ),
                "primaryNodeIpAddress": (
                    normalize_ip_address(
                        primary_node_ip_address,
                        field_name="primary_node_ip_address",
                    )
                    if primary_node_ip_address is not None
                    else None
                ),
                "ignoreCertificateErrors": ignore_certificate_errors,
            },
        )

    @mcp.tool
    async def dns_leave_cluster(
        force_leave: bool | None = None,
        confirm: bool = False,
        acknowledge: str | None = None,
    ) -> dict[str, Any]:
        require_destructive_confirmation(confirm=confirm)
        _critical_cluster_confirmation(confirm=confirm, acknowledge=acknowledge)
        return await client.call_or_throw(
            LEAVE_CLUSTER_ENDPOINT.api_path,
            {"forceLeave": force_leave},
        )

    @mcp.tool
    async def dns_notify_cluster(
        primary_node_id: int | str,
        primary_node_url: str,
        primary_node_ip_addresses: list[str] | str,
        confirm: bool = False,
        acknowledge: str | None = None,
    ) -> dict[str, Any]:
        _critical_cluster_confirmation(confirm=confirm, acknowledge=acknowledge)
        return await client.call_or_throw(
            NOTIFY_CLUSTER_ENDPOINT.api_path,
            {
                "primaryNodeId": _required_int(primary_node_id, field_name="primary_node_id"),
                "primaryNodeUrl": normalize_name(primary_node_url, field_name="primary_node_url"),
                "primaryNodeIpAddresses": _csv_ip_addresses(
                    primary_node_ip_addresses,
                    field_name="primary_node_ip_addresses",
                ),
            },
        )

    @mcp.tool
    async def dns_resync_cluster(
        confirm: bool = False,
        acknowledge: str | None = None,
    ) -> dict[str, Any]:
        _critical_cluster_confirmation(confirm=confirm, acknowledge=acknowledge)
        return await client.call_or_throw(RESYNC_CLUSTER_ENDPOINT.api_path)

    @mcp.tool
    async def dns_update_cluster_primary_node(
        primary_node_url: str,
        primary_node_ip_addresses: list[str] | str | None = None,
        confirm: bool = False,
        acknowledge: str | None = None,
    ) -> dict[str, Any]:
        _critical_cluster_confirmation(confirm=confirm, acknowledge=acknowledge)
        return await client.call_or_throw(
            UPDATE_CLUSTER_PRIMARY_NODE_ENDPOINT.api_path,
            {
                "primaryNodeUrl": normalize_name(primary_node_url, field_name="primary_node_url"),
                "primaryNodeIpAddresses": (
                    _csv_ip_addresses(
                        primary_node_ip_addresses,
                        field_name="primary_node_ip_addresses",
                    )
                    if primary_node_ip_addresses is not None
                    else None
                ),
            },
        )

    @mcp.tool
    async def dns_promote_to_cluster_primary(
        force_delete_primary: bool | None = None,
        confirm: bool = False,
        acknowledge: str | None = None,
    ) -> dict[str, Any]:
        _critical_cluster_confirmation(confirm=confirm, acknowledge=acknowledge)
        return await client.call_or_throw(
            PROMOTE_TO_CLUSTER_PRIMARY_ENDPOINT.api_path,
            {"forceDeletePrimary": force_delete_primary},
        )

    @mcp.tool
    async def dns_update_cluster_node_ip_addresses(
        ip_addresses: list[str] | str,
        confirm: bool = False,
        acknowledge: str | None = None,
    ) -> dict[str, Any]:
        _critical_cluster_confirmation(confirm=confirm, acknowledge=acknowledge)
        return await client.call_or_throw(
            UPDATE_CLUSTER_NODE_IP_ADDRESSES_ENDPOINT.api_path,
            {"ipAddresses": _csv_ip_addresses(ip_addresses, field_name="ip_addresses")},
        )
