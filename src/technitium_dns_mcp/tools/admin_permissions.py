from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from fastmcp import FastMCP

from technitium_dns_mcp.client.base import TechnitiumClient
from technitium_dns_mcp.client.endpoint_catalog import get_endpoint
from technitium_dns_mcp.client.models import RequestParam
from technitium_dns_mcp.guards import require_critical_admin_confirmation
from technitium_dns_mcp.validation import normalize_bool, normalize_name

LIST_ADMIN_PERMISSIONS_ENDPOINT = get_endpoint("dns_list_admin_permissions")
GET_ADMIN_PERMISSION_ENDPOINT = get_endpoint("dns_get_admin_permission")
SET_ADMIN_PERMISSION_ENDPOINT = get_endpoint("dns_set_admin_permission")
ADMIN_PERMISSIONS_ACKNOWLEDGEMENT = "admin-permissions"


def _permission_name(entry: Mapping[str, object], *, field_name: str) -> str:
    raw_name = entry.get("name")
    if not isinstance(raw_name, str):
        raise ValueError(f"{field_name}.name is required")
    return normalize_name(raw_name, field_name=f"{field_name}.name")


def _permission_flag(
    entry: Mapping[str, object],
    *,
    snake_key: str,
    camel_key: str,
    field_name: str,
) -> bool:
    raw_value = entry.get(snake_key, entry.get(camel_key, False))
    if not isinstance(raw_value, (bool, str)):
        raise ValueError(f"{field_name}.{snake_key} must be a boolean value")
    return normalize_bool(raw_value, field_name=f"{field_name}.{snake_key}")


def _normalize_permission_entries(
    value: str | Sequence[Mapping[str, object]] | None,
    *,
    field_name: str,
) -> RequestParam:
    if value is None:
        return None
    if isinstance(value, str):
        return normalize_name(value, field_name=field_name)

    normalized_entries: list[str] = []
    for index, entry in enumerate(value):
        item_name = _permission_name(entry, field_name=f"{field_name}[{index}]")
        can_view = _permission_flag(
            entry,
            snake_key="can_view",
            camel_key="canView",
            field_name=f"{field_name}[{index}]",
        )
        can_modify = _permission_flag(
            entry,
            snake_key="can_modify",
            camel_key="canModify",
            field_name=f"{field_name}[{index}]",
        )
        can_delete = _permission_flag(
            entry,
            snake_key="can_delete",
            camel_key="canDelete",
            field_name=f"{field_name}[{index}]",
        )
        normalized_entries.append(
            "|".join(
                [
                    item_name,
                    "true" if can_view else "false",
                    "true" if can_modify else "false",
                    "true" if can_delete else "false",
                ]
            )
        )
    return "|".join(normalized_entries)


def register_admin_permission_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_list_admin_permissions() -> dict[str, Any]:
        return await client.call_or_throw(LIST_ADMIN_PERMISSIONS_ENDPOINT.api_path)

    @mcp.tool
    async def dns_get_admin_permission(
        section: str,
        include_users_and_groups: bool | None = None,
    ) -> dict[str, Any]:
        return await client.call_or_throw(
            GET_ADMIN_PERMISSION_ENDPOINT.api_path,
            {
                "section": normalize_name(section, field_name="section"),
                "includeUsersAndGroups": include_users_and_groups,
            },
        )


def register_admin_permission_mutation_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_set_admin_permission(
        section: str,
        user_permissions: str | list[dict[str, object]] | None = None,
        group_permissions: str | list[dict[str, object]] | None = None,
        confirm: bool = False,
        acknowledge: str | None = None,
    ) -> dict[str, Any]:
        require_critical_admin_confirmation(
            confirm=confirm,
            acknowledge=acknowledge,
            expected_acknowledgement=ADMIN_PERMISSIONS_ACKNOWLEDGEMENT,
        )
        return await client.call_or_throw(
            SET_ADMIN_PERMISSION_ENDPOINT.api_path,
            {
                "section": normalize_name(section, field_name="section"),
                "userPermissions": _normalize_permission_entries(
                    user_permissions,
                    field_name="user_permissions",
                ),
                "groupPermissions": _normalize_permission_entries(
                    group_permissions,
                    field_name="group_permissions",
                ),
            },
        )
