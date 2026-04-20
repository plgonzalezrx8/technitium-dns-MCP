from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from technitium_dns_mcp.client.base import TechnitiumClient
from technitium_dns_mcp.client.endpoint_catalog import get_endpoint
from technitium_dns_mcp.client.models import RequestParam
from technitium_dns_mcp.guards import (
    require_critical_admin_confirmation,
    require_destructive_confirmation,
)
from technitium_dns_mcp.validation import (
    normalize_csv_names,
    normalize_name,
    normalize_optional_name,
    normalize_passthrough_params,
)

LIST_ADMIN_GROUPS_ENDPOINT = get_endpoint("dns_list_admin_groups")
CREATE_ADMIN_GROUP_ENDPOINT = get_endpoint("dns_create_admin_group")
GET_ADMIN_GROUP_ENDPOINT = get_endpoint("dns_get_admin_group")
SET_ADMIN_GROUP_ENDPOINT = get_endpoint("dns_set_admin_group")
DELETE_ADMIN_GROUP_ENDPOINT = get_endpoint("dns_delete_admin_group")
ADMIN_GROUPS_ACKNOWLEDGEMENT = "admin-groups"


def _group_name(group: str) -> str:
    return normalize_name(group, field_name="group")


def _normalize_group_options(options: dict[str, object] | None) -> dict[str, RequestParam]:
    normalized = normalize_passthrough_params(options, field_name="options")
    if options is None:
        return normalized

    members = options.get("members")
    if isinstance(members, (list, tuple, str)):
        normalized["members"] = normalize_csv_names(members, field_name="options.members")
    return normalized


def register_admin_group_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_list_admin_groups() -> dict[str, Any]:
        return await client.call_or_throw(LIST_ADMIN_GROUPS_ENDPOINT.api_path)

    @mcp.tool
    async def dns_get_admin_group(
        group: str,
        include_users: bool | None = None,
    ) -> dict[str, Any]:
        return await client.call_or_throw(
            GET_ADMIN_GROUP_ENDPOINT.api_path,
            {
                "group": _group_name(group),
                "includeUsers": include_users,
            },
        )


def register_admin_group_mutation_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_create_admin_group(
        group: str,
        description: str | None = None,
        confirm: bool = False,
        acknowledge: str | None = None,
    ) -> dict[str, Any]:
        require_critical_admin_confirmation(
            confirm=confirm,
            acknowledge=acknowledge,
            expected_acknowledgement=ADMIN_GROUPS_ACKNOWLEDGEMENT,
        )
        return await client.call_or_throw(
            CREATE_ADMIN_GROUP_ENDPOINT.api_path,
            {
                "group": _group_name(group),
                "description": normalize_optional_name(description, field_name="description"),
            },
        )

    @mcp.tool
    async def dns_set_admin_group(
        group: str,
        options: dict[str, object] | None = None,
        confirm: bool = False,
        acknowledge: str | None = None,
    ) -> dict[str, Any]:
        require_critical_admin_confirmation(
            confirm=confirm,
            acknowledge=acknowledge,
            expected_acknowledgement=ADMIN_GROUPS_ACKNOWLEDGEMENT,
        )
        return await client.call_or_throw(
            SET_ADMIN_GROUP_ENDPOINT.api_path,
            {"group": _group_name(group), **_normalize_group_options(options)},
        )

    @mcp.tool
    async def dns_delete_admin_group(
        group: str,
        confirm: bool = False,
        acknowledge: str | None = None,
    ) -> dict[str, Any]:
        require_destructive_confirmation(confirm=confirm)
        require_critical_admin_confirmation(
            confirm=confirm,
            acknowledge=acknowledge,
            expected_acknowledgement=ADMIN_GROUPS_ACKNOWLEDGEMENT,
        )
        return await client.call_or_throw(
            DELETE_ADMIN_GROUP_ENDPOINT.api_path,
            {"group": _group_name(group)},
        )
