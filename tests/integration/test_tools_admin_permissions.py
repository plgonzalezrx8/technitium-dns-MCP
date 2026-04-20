from urllib.parse import parse_qs

import pytest
from fastmcp import Client

from technitium_dns_mcp.app import build_mcp_server


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tool_name", "endpoint", "payload", "response"),
    [
        (
            "dns_list_admin_permissions",
            "/api/admin/permissions/list",
            {},
            {"permissions": [{"section": "Administration"}]},
        ),
        (
            "dns_get_admin_permission",
            "/api/admin/permissions/get",
            {"section": "Administration", "include_users_and_groups": True},
            {"section": "Administration", "groupPermissions": []},
        ),
    ],
)
async def test_admin_permission_read_tools_call_expected_endpoints(
    monkeypatch: pytest.MonkeyPatch,
    httpx_mock,
    *,
    tool_name: str,
    endpoint: str,
    payload: dict[str, object],
    response: dict[str, object],
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    httpx_mock.add_response(
        url=f"http://dns.local:5380{endpoint}",
        json={"status": "ok", "response": response},
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(tool_name, payload)

    assert result.data == response
    request = httpx_mock.get_request()
    assert request is not None
    expected = {"token": ["token-123"]}
    if "section" in payload:
        expected["section"] = [payload["section"]]  # type: ignore[index]
    if "include_users_and_groups" in payload:
        expected["includeUsersAndGroups"] = ["true"]
    assert parse_qs(request.content.decode()) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        {"section": "Administration", "confirm": False},
        {"section": "Administration", "confirm": True, "acknowledge": "wrong"},
    ],
)
async def test_admin_permission_set_tool_requires_critical_confirmation(
    monkeypatch: pytest.MonkeyPatch,
    *,
    payload: dict[str, object],
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")

    async with Client(build_mcp_server()) as client:
        with pytest.raises(Exception, match='acknowledge="admin-permissions"|confirm=True'):
            await client.call_tool("dns_set_admin_permission", payload)


@pytest.mark.asyncio
async def test_admin_permission_set_tool_posts_expected_payload(
    monkeypatch: pytest.MonkeyPatch,
    httpx_mock,
) -> None:
    monkeypatch.setenv("TECHNITIUM_URL", "http://dns.local:5380")
    monkeypatch.setenv("TECHNITIUM_TOKEN", "token-123")
    monkeypatch.setenv("TECHNITIUM_READONLY", "false")
    httpx_mock.add_response(
        url="http://dns.local:5380/api/admin/permissions/set",
        json={"status": "ok", "response": {"section": "Administration"}},
    )

    async with Client(build_mcp_server()) as client:
        result = await client.call_tool(
            "dns_set_admin_permission",
            {
                "section": "Administration",
                "user_permissions": [
                    {
                        "name": "alice",
                        "can_view": True,
                        "can_modify": True,
                        "can_delete": False,
                    }
                ],
                "group_permissions": [
                    {
                        "name": "admins",
                        "can_view": True,
                        "can_modify": True,
                        "can_delete": True,
                    }
                ],
                "confirm": True,
                "acknowledge": "admin-permissions",
            },
        )

    assert result.data == {"section": "Administration"}
    request = httpx_mock.get_request()
    assert request is not None
    assert parse_qs(request.content.decode()) == {
        "token": ["token-123"],
        "section": ["Administration"],
        "userPermissions": ["alice|true|true|false"],
        "groupPermissions": ["admins|true|true|true"],
    }
