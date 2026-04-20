from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from technitium_dns_mcp.client.base import TechnitiumClient
from technitium_dns_mcp.client.endpoint_catalog import get_endpoint
from technitium_dns_mcp.guards import (
    require_critical_admin_confirmation,
    require_destructive_confirmation,
)
from technitium_dns_mcp.validation import normalize_name

LIST_ADMIN_SESSIONS_ENDPOINT = get_endpoint("dns_list_admin_sessions")
CREATE_ADMIN_API_TOKEN_ENDPOINT = get_endpoint("dns_create_admin_api_token")
DELETE_ADMIN_SESSION_ENDPOINT = get_endpoint("dns_delete_admin_session")
ADMIN_SESSIONS_ACKNOWLEDGEMENT = "admin-sessions"


def register_admin_session_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_list_admin_sessions() -> dict[str, Any]:
        return await client.call_or_throw(LIST_ADMIN_SESSIONS_ENDPOINT.api_path)


def register_admin_session_mutation_tools(mcp: FastMCP, client: TechnitiumClient) -> None:
    @mcp.tool
    async def dns_create_admin_api_token(
        user: str,
        token_name: str,
        confirm: bool = False,
        acknowledge: str | None = None,
    ) -> dict[str, Any]:
        require_critical_admin_confirmation(
            confirm=confirm,
            acknowledge=acknowledge,
            expected_acknowledgement=ADMIN_SESSIONS_ACKNOWLEDGEMENT,
        )
        return await client.call_or_throw(
            CREATE_ADMIN_API_TOKEN_ENDPOINT.api_path,
            {
                "user": normalize_name(user, field_name="user"),
                "tokenName": normalize_name(token_name, field_name="token_name"),
            },
        )

    @mcp.tool
    async def dns_delete_admin_session(
        partial_token: str,
        confirm: bool = False,
        acknowledge: str | None = None,
    ) -> dict[str, Any]:
        require_destructive_confirmation(confirm=confirm)
        require_critical_admin_confirmation(
            confirm=confirm,
            acknowledge=acknowledge,
            expected_acknowledgement=ADMIN_SESSIONS_ACKNOWLEDGEMENT,
        )
        return await client.call_or_throw(
            DELETE_ADMIN_SESSION_ENDPOINT.api_path,
            {"partialToken": normalize_name(partial_token, field_name="partial_token")},
        )
