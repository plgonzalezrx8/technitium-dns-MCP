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

LIST_ADMIN_USERS_ENDPOINT = get_endpoint("dns_list_admin_users")
CREATE_ADMIN_USER_ENDPOINT = get_endpoint("dns_create_admin_user")
GET_ADMIN_USER_ENDPOINT = get_endpoint("dns_get_admin_user")
SET_ADMIN_USER_ENDPOINT = get_endpoint("dns_set_admin_user")
DELETE_ADMIN_USER_ENDPOINT = get_endpoint("dns_delete_admin_user")
ADMIN_USERS_ACKNOWLEDGEMENT = "admin-users"


def _user_name(user: str) -> str:
    return normalize_name(user, field_name="user")


def _normalize_user_options(options: dict[str, object] | None) -> dict[str, RequestParam]:
    normalized = normalize_passthrough_params(options, field_name="options")
    if options is None:
        return normalized

    member_of_groups = options.get("memberOfGroups")
    if isinstance(member_of_groups, (list, tuple, str)):
        normalized["memberOfGroups"] = normalize_csv_names(
            member_of_groups,
            field_name="options.memberOfGroups",
        )
    return normalized


def register_admin_user_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_list_admin_users() -> dict[str, Any]:
        return await client.call_or_throw(LIST_ADMIN_USERS_ENDPOINT.api_path)

    @mcp.tool
    async def dns_get_admin_user(
        user: str,
        include_groups: bool | None = None,
    ) -> dict[str, Any]:
        return await client.call_or_throw(
            GET_ADMIN_USER_ENDPOINT.api_path,
            {
                "user": _user_name(user),
                "includeGroups": include_groups,
            },
        )


def register_admin_user_mutation_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_create_admin_user(
        user: str,
        password: str,
        display_name: str | None = None,
        confirm: bool = False,
        acknowledge: str | None = None,
    ) -> dict[str, Any]:
        require_critical_admin_confirmation(
            confirm=confirm,
            acknowledge=acknowledge,
            expected_acknowledgement=ADMIN_USERS_ACKNOWLEDGEMENT,
        )
        return await client.call_or_throw(
            CREATE_ADMIN_USER_ENDPOINT.api_path,
            {
                "user": _user_name(user),
                "pass": normalize_name(password, field_name="password"),
                "displayName": normalize_optional_name(display_name, field_name="display_name"),
            },
        )

    @mcp.tool
    async def dns_set_admin_user(
        user: str,
        options: dict[str, object] | None = None,
        confirm: bool = False,
        acknowledge: str | None = None,
    ) -> dict[str, Any]:
        require_critical_admin_confirmation(
            confirm=confirm,
            acknowledge=acknowledge,
            expected_acknowledgement=ADMIN_USERS_ACKNOWLEDGEMENT,
        )
        return await client.call_or_throw(
            SET_ADMIN_USER_ENDPOINT.api_path,
            {"user": _user_name(user), **_normalize_user_options(options)},
        )

    @mcp.tool
    async def dns_delete_admin_user(
        user: str,
        confirm: bool = False,
        acknowledge: str | None = None,
    ) -> dict[str, Any]:
        require_destructive_confirmation(confirm=confirm)
        require_critical_admin_confirmation(
            confirm=confirm,
            acknowledge=acknowledge,
            expected_acknowledgement=ADMIN_USERS_ACKNOWLEDGEMENT,
        )
        return await client.call_or_throw(
            DELETE_ADMIN_USER_ENDPOINT.api_path,
            {"user": _user_name(user)},
        )
